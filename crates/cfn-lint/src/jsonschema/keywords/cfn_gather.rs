use super::super::{ValidationError, Validator};
use crate::ast::AstNode;

/// cfnGather keyword handler: gathers properties from related resources and validates
/// the gathered object against an inner schema.
///
/// The `constraint` is the cfnGather spec: `{"gather": {...}, "schema": {...}}`.
/// - `gather`: defines sources — each source specifies a reference path to follow
///   and properties to extract from the target resource.
/// - `schema`: the inner JSON Schema to validate the gathered object against,
///   potentially containing `$data`/`$lookup` references resolved against gathered data.
pub fn validate_cfn_gather(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    use crate::ast::{ObjectEntry, ObjectNode, Span, StringNode};
    use crate::engine::{follow_pointer, ref_to_resource_name, resolve_data_refs};
    use crate::resolver::Resolver;

    let gather_spec = match constraint.get("gather").and_then(|g| g.as_object()) {
        Some(g) => g,
        None => return vec![],
    };
    let inner_schema = match constraint.get("schema") {
        Some(s) => s,
        None => return vec![],
    };

    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![],
    };

    let resolver = Resolver::new(ctx);

    let empty_props = AstNode::Object(ObjectNode {
        entries: Vec::new(),
        span: Span::default(),
    });

    // Build gathered data object from gather spec
    let mut gathered_entries: Vec<ObjectEntry> = Vec::new();
    let mut all_resolved = true;

    for (source_name, source_spec) in gather_spec {
        let source_obj = match source_spec.as_object() {
            Some(o) => o,
            None => continue,
        };

        let (target_props, target_resource_type) =
            if let Some(ref_path) = source_obj.get("reference").and_then(|v| v.as_str()) {
                // Follow reference to find target resource
                let ref_node = match follow_pointer(node, ref_path) {
                    Some(n) => n,
                    None => {
                        all_resolved = false;
                        continue;
                    }
                };
                let target_name = match ref_to_resource_name(ref_node) {
                    Some(n) => n,
                    None => {
                        all_resolved = false;
                        continue;
                    }
                };
                let target_res = match ctx.template.resources.get(&target_name) {
                    Some(r) => r,
                    None => {
                        all_resolved = false;
                        continue;
                    }
                };
                // Check filter type if specified
                if let Some(filter_type) = source_obj
                    .get("filter")
                    .and_then(|f| f.get("type"))
                    .and_then(|t| t.as_str())
                {
                    if target_res.resource_type != filter_type {
                        all_resolved = false;
                        continue;
                    }
                }
                let rt = Some(target_res.resource_type.as_str());
                match &target_res.properties {
                    Some(p) => (p as &AstNode, rt),
                    None => (&empty_props as &AstNode, rt),
                }
            } else {
                // Self-reference: use current resource's properties (the node being validated)
                // Derive resource type from path (Resources/<name>/Properties → look up name)
                let self_type: Option<&str> = if path.len() >= 2 && path[0] == "Resources" {
                    ctx.template
                        .resources
                        .get(&path[1])
                        .map(|r| r.resource_type.as_str())
                } else {
                    None
                };
                (node, self_type)
            };

        // Extract specified properties
        let prop_specs = match source_obj.get("properties").and_then(|p| p.as_object()) {
            Some(p) => p,
            None => {
                // Source with no properties — add empty object
                gathered_entries.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: source_name.clone(),
                        span: Span::default(),
                    }),
                    key: source_name.clone(),
                    value: AstNode::Object(ObjectNode {
                        entries: Vec::new(),
                        span: node.span(),
                    }),
                    key_span: Span::default(),
                });
                continue;
            }
        };

        let mut source_entries: Vec<ObjectEntry> = Vec::new();
        for (prop_name, prop_spec) in prop_specs {
            // Handle $type: return the target resource type
            if prop_spec.as_str() == Some("$type") {
                if let Some(rt) = target_resource_type {
                    source_entries.push(ObjectEntry {
                        key_node: AstNode::String(StringNode {
                            value: prop_name.clone(),
                            span: Span::default(),
                        }),
                        key: prop_name.clone(),
                        value: AstNode::String(StringNode {
                            value: rt.to_string(),
                            span: Span::default(),
                        }),
                        key_span: Span::default(),
                    });
                }
                continue;
            }
            let extracted = extract_gather_property_inline(target_props, prop_spec, &resolver);
            if let Some(val) = extracted {
                source_entries.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: prop_name.clone(),
                        span: Span::default(),
                    }),
                    key: prop_name.clone(),
                    value: val,
                    key_span: Span::default(),
                });
            }
        }

        gathered_entries.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: source_name.clone(),
                span: Span::default(),
            }),
            key: source_name.clone(),
            value: AstNode::Object(ObjectNode {
                entries: source_entries,
                span: node.span(),
            }),
            key_span: Span::default(),
        });
    }

    if !all_resolved {
        return vec![];
    }

    let gathered = AstNode::Object(ObjectNode {
        entries: gathered_entries,
        span: node.span(),
    });

    // Resolve $data references in the schema
    let resolved_schema = resolve_data_refs(inner_schema, &gathered);

    // Strip cfnContext wrapper and apply context (e.g. functions=[])
    let has_cfn_ctx_functions = resolved_schema
        .get("cfnContext")
        .and_then(|c| c.get("functions"))
        .and_then(|f| f.as_array())
        .is_some();
    let final_schema = if let Some(cfn_ctx) = resolved_schema
        .get("cfnContext")
        .and_then(|c| c.as_object())
    {
        cfn_ctx
            .get("schema")
            .cloned()
            .unwrap_or(serde_json::json!({}))
    } else {
        resolved_schema
    };

    // Validate gathered data against the resolved inner schema.
    // Use a validator with empty functions list so Ref/GetAtt are treated as literal objects.
    let v = validator.without_cfn_lint_rules();
    let v = if has_cfn_ctx_functions {
        if let Some(ctx) = &v.context {
            let new_ctx = ctx.evolve(crate::context::ContextOptions {
                functions: Some(vec![]),
                ..Default::default()
            });
            Validator::new_with_context(v.root_schema().clone(), std::sync::Arc::new(new_ctx))
        } else {
            v
        }
    } else {
        v
    };

    v.validate(&gathered, &final_schema, path)
}

/// Extract a property value from a resource's properties using a gather property spec.
/// Inline version for keyword handler (avoids needing engine module dependency cycle).
fn extract_gather_property_inline(
    props: &AstNode,
    spec: &serde_json::Value,
    resolver: &crate::resolver::Resolver,
) -> Option<AstNode> {
    use crate::engine::{follow_pointer, json_to_ast, resolve_functions};

    let (path, default_val) = match spec {
        serde_json::Value::String(s) => (s.as_str(), None),
        serde_json::Value::Object(obj) => {
            let path = obj.get("path").and_then(|v| v.as_str()).unwrap_or("");
            let default_val = obj.get("default");
            (path, default_val)
        }
        _ => return None,
    };

    let raw = follow_pointer(props, path);
    match raw {
        Some(node) => {
            let resolved = resolve_functions(node, resolver);
            Some(resolved)
        }
        None => default_val.map(json_to_ast),
    }
}
