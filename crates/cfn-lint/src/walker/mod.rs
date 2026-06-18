mod function_types;

use std::sync::{Arc, LazyLock};

use regex::Regex;

use crate::ast::{AstNode, FunctionNode};
use crate::context::Context;
use crate::engine::{
    build_resource_properties_schema, expand_fn_if_branches, flatten_validation_errors,
    is_templated_property, keyword_to_rule_id,
};
use crate::getatts;
use crate::jsonschema::Validator;
use crate::jsonschema::cfn_lint_keyword::KeywordRuleRegistry;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static RE_RESOURCE_NAME: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[a-zA-Z0-9]+$").unwrap());

pub struct TemplateWalker {
    keyword_rules: Arc<KeywordRuleRegistry>,
    schema_provider: Option<Arc<dyn cfn_schema::SchemaProvider>>,
    strict_types: bool,
}

impl TemplateWalker {
    pub fn new(
        keyword_rules: Arc<KeywordRuleRegistry>,
        schema_provider: Option<Arc<dyn cfn_schema::SchemaProvider>>,
        strict_types: bool,
    ) -> Self {
        Self { keyword_rules, schema_provider, strict_types }
    }

    pub fn walk(&self, template: &Template, root: &AstNode, regions: &[String]) -> Vec<ValidationError> {
        let mut issues = Vec::new();

        // Dispatch template-level rules (keyword "/") — these need full template access
        issues.extend(self.keyword_rules.validate_template_all(template, root));

        let region = regions.first().map(|s| s.as_str()).unwrap_or("us-east-1");

        // Build a context for inline function resolution (shared by walker + schema validation)
        let mut tmpl_for_ctx = template.clone();
        // Pre-compute valid GetAtt attributes for each resource
        if let Some(sp) = self.schema_provider.as_ref() {
            for res in tmpl_for_ctx.resources.values_mut() {
                if let Some(schema) = sp.get_resource_schema(&res.resource_type, region) {
                    res.valid_atts = getatts::get_valid_attributes(&schema.raw, &res.resource_type);
                }
            }
        }
        let tmpl_arc = Arc::new(tmpl_for_ctx);
        let mut ctx = Context::new(Arc::clone(&tmpl_arc));
        ctx.sat_conditions = Some(Arc::new(crate::conditions::Conditions::from_template(&tmpl_arc)));
        let ctx = if region != "us-east-1" {
            ctx.evolve(crate::context::ContextOptions {
                regions: Some(regions.to_vec()),
                ..Default::default()
            })
        } else {
            ctx
        };
        let ctx_arc = Arc::new(ctx);
        let validator = Validator::new_with_context(serde_json::json!({}), Arc::clone(&ctx_arc));

        // Check if E3012 strict mode is configured via metadata or engine setting
        let e3012_strict = self.strict_types || template.root
            .get("Metadata")
            .and_then(|m| m.get("cfn-lint"))
            .and_then(|c| c.get("config"))
            .and_then(|c| c.get("configure_rules"))
            .and_then(|c| c.get("E3012"))
            .and_then(|c| c.get("strict"))
            .and_then(|v| match v {
                AstNode::Bool(b) => Some(b.value),
                AstNode::String(s) => Some(s.value == "True" || s.value == "true"),
                _ => None,
            })
            .unwrap_or(false);

        // Template-level Metadata
        if let Some(metadata_node) = root.get("Metadata") {
            self.dispatch(
                &validator,
                "Metadata",
                metadata_node,
                &["Metadata".to_string()],
                &serde_json::Value::Bool(true),
                &mut issues,
            );

            if let Some(interface_node) = metadata_node.get("AWS::CloudFormation::Interface") {
                self.dispatch(
                    &validator,
                    "Metadata/AWS::CloudFormation::Interface",
                    interface_node,
                    &["Metadata".to_string(), "AWS::CloudFormation::Interface".to_string()],
                    &serde_json::Value::Bool(true),
                    &mut issues,
                );
            }
        }

        // Resources
        for (name, resource) in &template.resources {
            let Some(resource_node) = root.get("Resources").and_then(|r| r.get(name)) else {
                continue;
            };

            let resource_type = &resource.resource_type;

            // Skip property validation for resources with invalid names
            if !RE_RESOURCE_NAME.is_match(name) {
                continue;
            }

            // Load resource schema for this type.
            // None means: schema provider exists but type not found (triggers E3006).
            // When no schema provider exists, we skip schema-dependent validation entirely.
            let resource_schema = self.schema_provider.as_ref()
                .and_then(|sp| sp.get_resource_schema(resource_type, region));

            // Schema validation of Properties
            if let Some(rs) = resource_schema {
                let schema_raw = &rs.raw;
                if let Some(props_node) = &resource.properties {
                    if schema_raw.get("properties").is_some() {
                        let resource_schema_val = build_resource_properties_schema(schema_raw);

                        let branches = expand_fn_if_branches(
                            props_node,
                            vec!["Resources".to_string(), name.clone(), "Properties".to_string()],
                        );

                        let mut errors = Vec::new();
                        let schema_raw_owned = schema_raw.clone();
                        for (branch_node, branch_path) in &branches {
                            let mut v = Validator::new_with_context(schema_raw_owned.clone(), Arc::clone(&ctx_arc));
                            if e3012_strict {
                                v.strict_types = true;
                            }
                            errors.extend(v.validate(*branch_node, &resource_schema_val, branch_path));
                        }

                        for err in errors.into_iter().flat_map(flatten_validation_errors) {
                            if err.unknown { continue; }
                            let rule_id = keyword_to_rule_id(&err.keyword);
                            if rule_id == "E3012" && is_templated_property(&err.path, resource_type) {
                                continue;
                            }
                            let final_rule_id = if err.resolved_from_ref {
                                "W1030"
                            } else {
                                rule_id
                            };
                            issues.push(ValidationError::new(
                                final_rule_id,
                                err.message,
                                err.path,
                                err.span,
                            ));
                        }
                    }
                }
            }

            let instance_base = vec!["Resources".to_string(), name.to_string()];
            let type_base = vec!["Resources".to_string(), resource_type.to_string()];

            self.walk_node(
                &validator,
                resource_node,
                &instance_base,
                &type_base,
                None,
                resource_schema,
                &mut issues,
            );
        }

        // Outputs
        if let Some(outputs_node) = root.get("Outputs") {
            if let Some(obj) = outputs_node.as_object() {
                for (name, output_node) in obj.iter() {
                    let instance_path = vec!["Outputs".to_string(), name.to_string()];
                    let type_path = vec!["Outputs".to_string(), "*".to_string()];
                    self.walk_node(
                        &validator,
                        output_node,
                        &instance_path,
                        &type_path,
                        None,
                        None,
                        &mut issues,
                    );
                }
            }
        }

        // Parameters
        if let Some(params_node) = root.get("Parameters") {
            if let Some(obj) = params_node.as_object() {
                for (name, param_node) in obj.iter() {
                    let instance_path = vec!["Parameters".to_string(), name.to_string()];
                    let type_path = vec!["Parameters".to_string(), "*".to_string()];
                    self.walk_node(
                        &validator,
                        param_node,
                        &instance_path,
                        &type_path,
                        None,
                        None,
                        &mut issues,
                    );
                }
            }
        }

        // Post-walk type checks
        issues.extend(self.validate_output_getatt_types(template, root, region));
        issues.extend(self.validate_function_types(template, root, regions));

        issues
    }

    fn walk_node(
        &self,
        validator: &Validator,
        node: &AstNode,
        instance_path: &[String],
        type_path: &[String],
        schema_node: Option<&cfn_schema::SchemaNode>,
        resource_schema: Option<&cfn_schema::ResourceSchema>,
        issues: &mut Vec<ValidationError>,
    ) {
        static EMPTY_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| serde_json::json!({}));
        let type_keyword = type_path.join("/");
        let schema_raw = schema_node
            .map(|s| &s.raw)
            .or_else(|| resource_schema.map(|rs| &rs.raw))
            .unwrap_or(if self.schema_provider.is_some() { &serde_json::Value::Null } else { &EMPTY_SCHEMA });

        self.dispatch(validator, &type_keyword, node, instance_path, schema_raw, issues);

        match node {
            AstNode::Object(obj) => {
                for (key, child) in obj.iter() {
                    let mut child_inst = instance_path.to_vec();
                    child_inst.push(key.to_string());
                    let mut child_type = type_path.to_vec();
                    child_type.push(key.to_string());

                    // At Properties, enter the resource schema root
                    let child_schema = if key == "Properties" && schema_node.is_none() {
                        resource_schema.map(|rs| &rs.root)
                    } else {
                        schema_node.and_then(|s| s.properties.get(key))
                    };

                    self.walk_node(
                        validator,
                        child,
                        &child_inst,
                        &child_type,
                        child_schema,
                        resource_schema,
                        issues,
                    );
                }
            }
            AstNode::Array(arr) => {
                let items_schema = schema_node
                    .and_then(|s| s.items.as_deref());

                for (i, elem) in arr.elements.iter().enumerate() {
                    let mut child_inst = instance_path.to_vec();
                    child_inst.push(i.to_string());
                    let mut child_type = type_path.to_vec();
                    child_type.push("*".to_string());

                    self.walk_node(
                        validator,
                        elem,
                        &child_inst,
                        &child_type,
                        items_schema,
                        resource_schema,
                        issues,
                    );
                }
            }
            AstNode::Function(func) if func.name == "Fn::If" => {
                self.walk_fn_if(validator, func, instance_path, type_path, schema_node, resource_schema, issues);
            }
            AstNode::Function(_) => {}

            _ => {}
        }
    }

    fn walk_fn_if(
        &self,
        validator: &Validator,
        func: &FunctionNode,
        instance_path: &[String],
        type_path: &[String],
        schema_node: Option<&cfn_schema::SchemaNode>,
        resource_schema: Option<&cfn_schema::ResourceSchema>,
        issues: &mut Vec<ValidationError>,
    ) {
        let arr = match func.args.as_array() {
            Some(a) if a.elements.len() == 3 => a,
            _ => return,
        };

        let cond_name = match arr.elements[0].as_str() {
            Some(s) => s.to_string(),
            None => return,
        };

        let ctx = match validator.context() {
            Some(c) => c,
            None => return,
        };

        let scenarios = ctx.evaluate_condition(&cond_name);

        for scenario in &scenarios {
            let branch_idx = if scenario.value { 1 } else { 2 };
            let branch = &arr.elements[branch_idx];

            // Skip Ref AWS::NoValue branches
            if let AstNode::Function(f) = branch {
                if f.name == "Ref" && f.args.as_str() == Some("AWS::NoValue") {
                    continue;
                }
            }

            let branch_validator = Validator::new_with_context(
                serde_json::json!({}),
                Arc::new(scenario.context.clone()),
            );

            self.walk_node(
                &branch_validator,
                branch,
                instance_path,
                type_path,
                schema_node,
                resource_schema,
                issues,
            );
        }
    }

    fn dispatch(
        &self,
        validator: &Validator,
        path_keyword: &str,
        node: &AstNode,
        instance_path: &[String],
        schema: &serde_json::Value,
        issues: &mut Vec<ValidationError>,
    ) {
        for err in self.keyword_rules.dispatch(
            validator,
            path_keyword,
            node,
            schema,
            instance_path,
        ) {
            let rule_id = if err.keyword.starts_with("cfnLint:") {
                err.keyword.trim_start_matches("cfnLint:").to_string()
            } else if err.rule_id.is_some() {
                err.rule_id.clone().unwrap()
            } else {
                keyword_to_rule_id(&err.keyword).to_string()
            };
            issues.push(ValidationError::new(rule_id, err.message, err.path, err.span));
        }
    }


}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use std::sync::Arc;

    fn walk_yaml(yaml: &[u8]) -> Vec<ValidationError> {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = crate::template::Template::from_ast(&ast).unwrap();
        let registry = KeywordRuleRegistry::from_inventory();
        let walker = TemplateWalker::new(Arc::new(registry), None, false);
        walker.walk(&tmpl, &ast, &["us-east-1".to_string()])
    }

    #[test]
    fn empty_resources_no_crash() {
        let issues = walk_yaml(b"Resources:\n  Bucket:\n    Type: AWS::S3::Bucket\n");
        let _ = issues;
    }

    #[test]
    fn template_with_empty_resources() {
        let issues = walk_yaml(b"AWSTemplateFormatVersion: '2010-09-09'\nResources: {}\n");
        let _ = issues;
    }

    #[test]
    fn walks_outputs() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\nOutputs:\n  Out:\n    Value: !Ref B\n";
        let issues = walk_yaml(yaml);
        let _ = issues;
    }

    #[test]
    fn walks_parameters() {
        let yaml = b"Parameters:\n  Env:\n    Type: String\nResources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let issues = walk_yaml(yaml);
        let _ = issues;
    }

    #[test]
    fn fn_if_branches_walked() {
        let yaml = br#"
Conditions:
  IsProd: !Equals [!Ref Env, prod]
Parameters:
  Env:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !If [IsProd, prod-bucket, dev-bucket]
"#;
        let issues = walk_yaml(yaml);
        let _ = issues;
    }

    #[test]
    fn metadata_walked() {
        let yaml = br#"
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups: []
Resources:
  B:
    Type: AWS::S3::Bucket
"#;
        let issues = walk_yaml(yaml);
        let _ = issues;
    }

    #[test]
    fn unknown_resource_type_no_crash() {
        let yaml = b"Resources:\n  Custom:\n    Type: Custom::MyThing\n    Properties:\n      Foo: bar\n";
        let issues = walk_yaml(yaml);
        let _ = issues;
    }

    #[test]
    fn array_properties_walked() {
        let yaml = br#"
Resources:
  SG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: test
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
"#;
        let issues = walk_yaml(yaml);
        let _ = issues;
    }

    #[test]
    fn suppression_via_metadata() {
        let yaml = br#"
Metadata:
  cfn-lint:
    config:
      ignore_checks:
        - W2001
Parameters:
  Unused:
    Type: String
Resources:
  B:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = crate::template::Template::from_ast(&ast).unwrap();
        let mut engine = crate::engine::Engine::new();
        let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
        assert!(!issues.iter().any(|i| i.rule_id.as_deref() == Some("W2001")), "W2001 should be suppressed");
    }
}
