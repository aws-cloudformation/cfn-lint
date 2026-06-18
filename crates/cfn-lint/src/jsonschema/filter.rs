use std::sync::Arc;

use crate::ast::AstNode;
use crate::context::Context;

use super::Validator;

impl Validator {
    /// Keywords that need per-condition-scenario validation (Python's group_functions).
    /// These keywords are sensitive to Fn::If / Ref AWS::NoValue in property values.
    pub(super) const GROUP_KEYWORDS: &'static [&'static str] = &[
        "required", "dependentRequired", "dependentExcluded",
        "requiredXor", "requiredOr", "uniqueItems",
        "minItems", "maxItems", "minProperties", "maxProperties",
    ];

    /// When no context is set or the node is not a function, returns the
    /// original node unchanged.
    ///
    /// Python-style filter: replaces the schema to route functions to their
    /// keyword handlers. Does NOT resolve functions — that's done by the
    /// keyword handlers themselves (ref, fn_sub, fn_if, etc.).
    ///
    /// Returns (instance, modified_schema, validator) tuples.
    pub(super) fn filter(
        &self,
        node: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<(AstNode, serde_json::Value, Option<Arc<Context>>)> {
        // Dynamic references: replace schema with {"dynamicReference": schema}
        if let Some(s) = node.as_str() {
            if s.contains("{{resolve:") || s.contains("{{ resolve:") || s.contains("{{resolve :") {
                let modified = serde_json::json!({"dynamicReference": schema});
                return vec![(node.clone(), modified, None)];
            }
        }

        // cfnContext: evolve context and replace schema with inner schema,
        // then continue filter processing (including function routing)
        let (effective_schema, evolved_context) = if let Some(cfn_ctx) = schema.get("cfnContext").and_then(|v| v.as_object()) {
            let inner = cfn_ctx.get("schema").cloned().unwrap_or(serde_json::json!({}));
            if let Some(funcs) = cfn_ctx.get("functions").and_then(|f| f.as_array()) {
                let func_names: Vec<String> = funcs.iter().filter_map(|v| v.as_str().map(String::from)).collect();
                if let Some(ctx) = &self.context {
                    let new_ctx = ctx.evolve(crate::context::ContextOptions {
                        functions: Some(func_names),
                        ..Default::default()
                    });
                    (inner, Some(Arc::new(new_ctx)))
                } else {
                    let mut ctx = crate::context::Context::empty();
                    ctx.functions = Some(func_names);
                    (inner, Some(Arc::new(ctx)))
                }
            } else {
                (inner, None)
            }
        } else {
            (schema.clone(), None)
        };
        let schema = &effective_schema;

        // Functions: replace schema with {"fn_name": schema}
        // Only route if the function is allowed in the current context
        if let AstNode::Function(func) = node {
            let ctx_ref = evolved_context.as_ref().or(self.context.as_ref()); let is_allowed = match ctx_ref {
                Some(ctx) => match &ctx.functions {
                    Some(funcs) => funcs.contains(&func.name),
                    None => true, // No restriction
                },
                None => true,
            };
            if is_allowed {
                let keyword = match func.name.as_str() {
                    "Ref" => "ref",
                    "Fn::Sub" => "fn_sub",
                    "Fn::If" => "fn_if",
                    "Fn::GetAtt" => "fn_getatt",
                    "Fn::Join" => "fn_join",
                    "Fn::Select" => "fn_select",
                    "Fn::Split" => "fn_split",
                    "Fn::FindInMap" => "fn_findinmap",
                    "Fn::Base64" => "fn_base64",
                    "Fn::GetAZs" => "fn_getazs",
                    "Fn::ImportValue" => "fn_importvalue",
                    "Fn::Transform" => "fn_transform",
                    "Fn::ToJsonString" => "fn_tojsonstring",
                    "Fn::Length" => "fn_length",
                    "Fn::Cidr" => "fn_cidr",
                    "Fn::GetStackOutput" => "fn_getstackoutput",
                    "Fn::Equals" => "fn_equals",
                    "Fn::And" => "fn_condition",
                    "Fn::Or" => "fn_condition",
                    "Fn::Not" => "fn_condition",
                    "Condition" => "fn_condition",
                    _ => "fn_unknown",
                };
                let modified = serde_json::json!({keyword: schema});
                return vec![(node.clone(), modified, evolved_context)];
            }
            // Function not allowed in context — fall through to normal validation
        }

        // Check if the object has Fn::If property values that need per-scenario validation
        if let Some(obj) = node.as_object() {
            let has_conditional_props = obj.values().any(|v| {
                matches!(v, AstNode::Function(f) if f.name == "Fn::If" || (f.name == "Ref" && f.args.as_str() == Some("AWS::NoValue")))
            });

            if has_conditional_props {
                if let Some(schema_obj) = schema.as_object() {
                    let has_group = schema_obj.keys().any(|k| Self::GROUP_KEYWORDS.contains(&k.as_str()));
                    if has_group {
                        let mut standard = serde_json::Map::new();
                        let mut group = serde_json::Map::new();
                        for (k, v) in schema_obj {
                            if Self::GROUP_KEYWORDS.contains(&k.as_str()) {
                                group.insert(k.clone(), v.clone());
                            } else {
                                standard.insert(k.clone(), v.clone());
                            }
                        }

                        let mut results = Vec::new();

                        if !standard.is_empty() {
                            let mut std_schema = serde_json::Value::Object(standard);
                            if self.cfn_lint_rules.is_some() && !self.cfn_path.is_empty() {
                                let base_len = self.cfn_path.len();
                                let mut cfn_path_parts = self.cfn_path.clone();
                                if path.len() > base_len {
                                    cfn_path_parts.extend_from_slice(&path[base_len..]);
                                }
                                if let Some(o) = std_schema.as_object_mut() {
                                    let paths = o.entry("cfnLint").or_insert_with(|| serde_json::json!([]));
                                    if let Some(arr) = paths.as_array_mut() {
                                        arr.push(serde_json::Value::String(cfn_path_parts.join("/")));
                                    }
                                }
                            }
                            results.push((node.clone(), std_schema, evolved_context.clone()));
                        }

                        if !group.is_empty() {
                            let group_schema = serde_json::Value::Object(group);
                            let cond_state = self.context.as_ref()
                                .map(|c| c.condition_state.clone())
                                .unwrap_or_default();
                            let scenarios = resolve_object_conditions(obj, &cond_state);
                            for (resolved, scenario_state) in scenarios {
                                let evolved = self.context.as_ref().map(|ctx| {
                                    Arc::new(ctx.evolve(crate::context::ContextOptions {
                                        condition_state: Some(scenario_state),
                                        ..Default::default()
                                    }))
                                });
                                results.push((resolved, group_schema.clone(), evolved));
                            }
                        }

                        return results;
                    }
                }
            }
        }

        // Normal values: inject cfnLint keyword with current path if rules are registered
        let mut modified = schema.clone();

        if self.cfn_lint_rules.is_some() && !self.cfn_path.is_empty() {
            let base_len = self.cfn_path.len();
            let mut cfn_path_parts = self.cfn_path.clone();
            if path.len() > base_len {
                cfn_path_parts.extend_from_slice(&path[base_len..]);
            }
            let cfn_path_str = cfn_path_parts.join("/");
            if let Some(obj) = modified.as_object_mut() {
                let paths = obj.entry("cfnLint").or_insert_with(|| serde_json::json!([]));
                if let Some(arr) = paths.as_array_mut() {
                    arr.push(serde_json::Value::String(cfn_path_str));
                }

                // Inject patternProperties for free-form objects (type: object with no
                // properties/additionalProperties/patternProperties) to force descent.
                // Matches Python's _filter_schemas behavior for nested JSON objects.
                let is_object_type = obj.get("type").map_or(false, |t| {
                    t.as_str() == Some("object") || t.as_array().map_or(false, |a| a.iter().any(|v| v.as_str() == Some("object")))
                });
                if is_object_type
                    && !obj.contains_key("properties")
                    && !obj.contains_key("additionalProperties")
                    && !obj.contains_key("patternProperties")
                {
                    obj.insert("patternProperties".to_string(), serde_json::json!({
                        ".*": {"type": ["array", "boolean", "integer", "null", "number", "object", "string"]}
                    }));
                }
                let is_array_type = obj.get("type").map_or(false, |t| {
                    t.as_str() == Some("array") || t.as_array().map_or(false, |a| a.iter().any(|v| v.as_str() == Some("array")))
                });
                if is_array_type && !obj.contains_key("items") {
                    obj.insert("items".to_string(), serde_json::json!({"type": ["array", "boolean", "integer", "null", "number", "object", "string"]}));
                }
            }
            return vec![(node.clone(), modified, evolved_context)];
        }

        vec![(node.clone(), modified, evolved_context)]
    }
}

/// Resolve Fn::If in an object's property values, producing one AstNode per
/// condition scenario. Mirrors Python's `build_instance_from_scenario`.
///
/// For each Fn::If in a property value, generates scenarios where the condition
/// is true (use branch 1) and false (use branch 2). Properties whose resolved
/// value is Ref AWS::NoValue are removed from the object.
fn resolve_object_conditions(
    obj: &crate::ast::ObjectNode,
    condition_state: &std::collections::HashMap<String, bool>,
) -> Vec<(AstNode, std::collections::HashMap<String, bool>)> {
    // Collect condition names from Fn::If property values that aren't already pinned
    let mut conditions: Vec<String> = Vec::new();
    for val in obj.values() {
        if let AstNode::Function(f) = val {
            if f.name == "Fn::If" {
                if let Some(arr) = f.args.as_array() {
                    if arr.elements.len() == 3 {
                        if let Some(name) = arr.elements[0].as_str() {
                            if !condition_state.contains_key(name)
                                && !conditions.contains(&name.to_string())
                            {
                                conditions.push(name.to_string());
                            }
                        }
                    }
                }
            }
        }
    }

    // Build base scenario from already-pinned conditions
    let base_scenario: std::collections::HashMap<String, bool> = condition_state.clone();

    if conditions.is_empty() {
        return vec![(resolve_one_scenario(obj, &base_scenario), base_scenario)];
    }

    let n = conditions.len();
    let max = std::cmp::min(1usize << n, 128);
    let mut results = Vec::new();
    let mut seen_keys: Vec<Vec<String>> = Vec::new();
    for i in 0..max {
        let mut scenario = base_scenario.clone();
        for (j, name) in conditions.iter().enumerate() {
            scenario.insert(name.clone(), (i >> (n - 1 - j)) & 1 == 0);
        }
        let resolved = resolve_one_scenario(obj, &scenario);
        if let Some(robj) = resolved.as_object() {
            let mut keys: Vec<String> = robj.keys().map(|s| s.to_string()).collect();
            keys.sort();
            if !seen_keys.contains(&keys) {
                seen_keys.push(keys);
                results.push((resolved, scenario));
            }
        } else {
            results.push((resolved, scenario));
        }
    }
    results
}

/// Resolve a single condition scenario: pick Fn::If branches, remove NoValue properties.
fn resolve_one_scenario(
    obj: &crate::ast::ObjectNode,
    scenario: &std::collections::HashMap<String, bool>,
) -> AstNode {
    let mut new_entries: Vec<crate::ast::ObjectEntry> = Vec::new();
    for entry in &obj.entries {
        let resolved = resolve_value_for_scenario(&entry.value, scenario);
        if let Some(resolved) = resolved {
            new_entries.push(crate::ast::ObjectEntry {
                key_node: entry.key_node.clone(),
                key: entry.key.clone(),
                value: resolved,
                key_span: entry.key_span,
            });
        }
    }
    AstNode::Object(crate::ast::ObjectNode {
        entries: new_entries,
        span: obj.span,
    })
}

/// Resolve a value for a condition scenario. Returns None if the value is Ref AWS::NoValue.
fn resolve_value_for_scenario(
    node: &AstNode,
    scenario: &std::collections::HashMap<String, bool>,
) -> Option<AstNode> {
    if let AstNode::Function(f) = node {
        if f.name == "Ref" && f.args.as_str() == Some("AWS::NoValue") {
            return None;
        }
        if f.name == "Fn::If" {
            if let Some(arr) = f.args.as_array() {
                if arr.elements.len() == 3 {
                    if let Some(name) = arr.elements[0].as_str() {
                        if let Some(&val) = scenario.get(name) {
                            let branch = if val { &arr.elements[1] } else { &arr.elements[2] };
                            return resolve_value_for_scenario(branch, scenario);
                        }
                    }
                }
            }
        }
    }
    Some(node.clone())
}
