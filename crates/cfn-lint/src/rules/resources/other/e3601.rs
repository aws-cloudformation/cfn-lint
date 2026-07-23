/// E3601 — Validate the structure of a StepFunctions StateMachine definition.
///
/// Validates DefinitionString / Definition against the embedded statemachine schema.
use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::template::Template;

static STATEMACHINE_SCHEMA: LazyLock<Option<serde_json::Value>> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/step_functions/statemachine.json"
    ))
    .ok()
});

pub struct E3601;

impl CfnLintRule for E3601 {
    fn id(&self) -> &str {
        "E3601"
    }
    fn short_description(&self) -> &str {
        "Validate the structure of a StateMachine definition"
    }
    fn description(&self) -> &str {
        "Validate the Definition or DefinitionString inside a AWS::StepFunctions::StateMachine resource"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let resources = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let schema: &serde_json::Value = match STATEMACHINE_SCHEMA.as_ref() {
            Some(s) => s,
            None => return vec![],
        };

        let validator = Validator::new(schema.clone());
        let mut issues = Vec::new();

        for (name, node) in resources.iter() {
            match template.resources.get(name) {
                Some(r) if r.resource_type == "AWS::StepFunctions::StateMachine" => {}
                _ => continue,
            }

            let props = match node.get("Properties") {
                Some(p) => p,
                None => continue,
            };

            for key in &["DefinitionString", "Definition"] {
                let val = match props.get(key) {
                    Some(v) => v,
                    None => continue,
                };

                if val.as_function().is_some() {
                    continue;
                }

                let base_path: Vec<String> = vec![
                    "Resources".into(),
                    name.to_string(),
                    "Properties".into(),
                    key.to_string(),
                ];

                if let Some(s) = val.as_str() {
                    // Parse JSON string into AstNode for schema validation
                    if let Ok(parsed) = crate::parser::parse_json(s.as_bytes()) {
                        let errors = validator.validate(&parsed, schema, &base_path);
                        issues.extend(errors.into_iter().map(|err| ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: err.message,
                            path: err.path,
                            span: val.span(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        }));
                    }
                } else if val.as_object().is_some() {
                    let errors = validator.validate(val, schema, &base_path);
                    issues.extend(errors.into_iter().map(|err| ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: err.message,
                        path: err.path,
                        span: val.span(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    }));
                }
            }
        }

        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_definition_string() {
        let yaml = br#"
Resources:
  MyStateMachine:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      DefinitionString: '{"StartAt":"Hello","States":{"Hello":{"Type":"Pass","End":true}}}'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3601.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_missing_start_at() {
        let yaml = br#"
Resources:
  SM1:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      DefinitionString: '{"States":{"Hello":{"Type":"Pass","End":true}}}'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3601.validate_template(&tmpl, &ast);
        assert!(!issues.is_empty());
        assert!(issues.iter().any(|i| i.message.contains("StartAt")));
    }

    #[test]
    fn test_function_skipped() {
        let yaml = br#"
Resources:
  SM:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      DefinitionString: !Sub '{"StartAt":"Hello","States":{"Hello":{"Type":"Pass","End":true}}}'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3601.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_non_stepfunctions_resource_skipped() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3601.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3601);
