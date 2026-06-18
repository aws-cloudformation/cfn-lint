use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ContextEvolution, ValidationError, Validator};
use crate::rules::Severity;

/// The set of intrinsic functions allowed in Output Export Name context.
/// This is FUNCTIONS minus Fn::GetStackOutput (which Python excludes).
const EXPORT_NAME_FUNCTIONS: &[&str] = &[
    "Fn::Base64",
    "Fn::FindInMap",
    "Fn::GetAtt",
    "Fn::GetAZs",
    "Fn::If",
    "Fn::ImportValue",
    "Fn::Join",
    "Fn::Select",
    "Fn::Split",
    "Fn::Sub",
    "Fn::Transform",
    "Fn::ToJsonString",
    "Fn::Length",
    "Fn::Cidr",
    "Ref",
];

/// E6102: Validate that output exports have values of strings.
///
/// Output Export Name must resolve to a string type. Uses the schema engine
/// with an evolved context that restricts allowed functions (excluding
/// Fn::GetStackOutput) and validates against `{"type": "string"}`.
pub struct E6102;

impl CfnLintRule for E6102 {
    fn id(&self) -> &str {
        "E6102"
    }
    fn short_description(&self) -> &str {
        "Output export names must be strings"
    }
    fn description(&self) -> &str {
        "Make sure output exports have a value of type string"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Outputs/*/Export/Name"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Evolve context: restrict allowed functions (exclude Fn::GetStackOutput)
        let evolved = validator.evolve(ContextEvolution {
            functions: Some(
                EXPORT_NAME_FUNCTIONS
                    .iter()
                    .map(|s| s.to_string())
                    .collect(),
            ),
            ..Default::default()
        });

        // Validate through the schema engine with {"type": "string"}
        let schema = serde_json::json!({"type": "string"});
        let v = evolved.without_cfn_lint_rules();
        v.validate_schema(instance, &schema, path)
            .into_iter()
            .filter(|e| !e.unknown)
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::context::Context;
    use crate::jsonschema::Validator;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    fn make_validator(yaml: &[u8]) -> (Validator, AstNode) {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(tmpl);
        let mut v = Validator::new(serde_json::json!({}));
        v.context = Some(Arc::new(ctx));
        (v, ast)
    }

    #[test]
    fn test_string_export_name() {
        let yaml = br#"
Outputs:
  Out1:
    Value: val
    Export:
      Name: my-export
"#;
        let (validator, ast) = make_validator(yaml);
        let export_name = ast
            .get("Outputs")
            .unwrap()
            .get("Out1")
            .unwrap()
            .get("Export")
            .unwrap()
            .get("Name")
            .unwrap();
        let path = vec![
            "Outputs".into(),
            "Out1".into(),
            "Export".into(),
            "Name".into(),
        ];
        let errors = E6102.validate(
            &validator,
            "Outputs/*/Export/Name",
            export_name,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_array_export_name_fails() {
        let yaml = br#"
Outputs:
  Out1:
    Value: val
    Export:
      Name:
        - item1
        - item2
"#;
        let (validator, ast) = make_validator(yaml);
        let export_name = ast
            .get("Outputs")
            .unwrap()
            .get("Out1")
            .unwrap()
            .get("Export")
            .unwrap()
            .get("Name")
            .unwrap();
        let path = vec![
            "Outputs".into(),
            "Out1".into(),
            "Export".into(),
            "Name".into(),
        ];
        let errors = E6102.validate(
            &validator,
            "Outputs/*/Export/Name",
            export_name,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert_eq!(errors[0].keyword, "type");
    }

    #[test]
    fn test_number_export_name_coerces_to_string() {
        // In CloudFormation relaxed mode, numbers coerce to strings
        let yaml = br#"
Outputs:
  Out1:
    Value: val
    Export:
      Name: 123
"#;
        let (validator, ast) = make_validator(yaml);
        let export_name = ast
            .get("Outputs")
            .unwrap()
            .get("Out1")
            .unwrap()
            .get("Export")
            .unwrap()
            .get("Name")
            .unwrap();
        let path = vec![
            "Outputs".into(),
            "Out1".into(),
            "Export".into(),
            "Name".into(),
        ];
        let errors = E6102.validate(
            &validator,
            "Outputs/*/Export/Name",
            export_name,
            &serde_json::json!({}),
            &path,
        );
        assert!(
            errors.is_empty(),
            "Numbers should coerce to strings in relaxed mode"
        );
    }

    #[test]
    fn test_fn_sub_export_name_allowed() {
        let yaml = br#"
Outputs:
  Out1:
    Value: val
    Export:
      Name: !Sub "${AWS::StackName}-export"
"#;
        let (validator, ast) = make_validator(yaml);
        let export_name = ast
            .get("Outputs")
            .unwrap()
            .get("Out1")
            .unwrap()
            .get("Export")
            .unwrap()
            .get("Name")
            .unwrap();
        let path = vec![
            "Outputs".into(),
            "Out1".into(),
            "Export".into(),
            "Name".into(),
        ];
        let errors = E6102.validate(
            &validator,
            "Outputs/*/Export/Name",
            export_name,
            &serde_json::json!({}),
            &path,
        );
        assert!(
            errors.is_empty(),
            "Fn::Sub should be allowed in export names"
        );
    }
}

crate::register_cfn_lint_rule!(E6102);
