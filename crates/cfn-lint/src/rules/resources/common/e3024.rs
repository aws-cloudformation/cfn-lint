use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::engine::flatten_validation_errors;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::template::Template;

static TAGGING_SCHEMA: LazyLock<Option<serde_json::Value>> = LazyLock::new(|| {
    let schema_str = include_str!("../../../../data/schemas/other/resources/tagging.json");
    serde_json::from_str(schema_str).ok()
});

/// E3024: Validate tag configuration.
///
/// Validates tag values against the tagging.json schema when the resource
/// schema indicates it is taggable. Checks unique keys, aws: prefix,
/// key/value lengths via schema validation.
pub struct E3024;

impl CfnLintRule for E3024 {
    fn id(&self) -> &str {
        "E3024"
    }
    fn short_description(&self) -> &str {
        "Validate tag configuration"
    }
    fn description(&self) -> &str {
        "Validates tag values to make sure they have unique keys and they follow pattern requirements"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let is_taggable = schema
            .get("tagging")
            .and_then(|t| t.get("taggable"))
            .and_then(|t| t.as_bool())
            == Some(true);
        if !is_taggable {
            return vec![];
        }

        let tagging_schema = match TAGGING_SCHEMA.as_ref() {
            Some(s) => s,
            None => return vec![],
        };

        let props_node = match instance.get("Properties") {
            Some(p) => p,
            None => return vec![],
        };

        let mut tag_path = path.to_vec();
        tag_path.push("Properties".to_string());

        let v = validator.without_cfn_lint_rules();
        v.validate_schema(props_node, tagging_schema, &tag_path)
            .into_iter()
            .flat_map(flatten_validation_errors)
            .filter(|e| !e.unknown)
            .map(|e| ValidationError::new(self.id(), e.message, e.path, e.span))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use crate::engine::Engine;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_valid_tags() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      Tags:
        - Key: Environment
          Value: Production
        - Key: Team
          Value: Platform
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let mut engine = Engine::new();
        let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
        let e3024: Vec<_> = issues
            .iter()
            .filter(|i| i.rule_id.as_deref() == Some("E3024"))
            .collect();
        assert!(e3024.is_empty());
    }

    #[test]
    fn test_duplicate_tag_keys_no_schema() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      Tags:
        - Key: Environment
          Value: Production
        - Key: Environment
          Value: Staging
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let mut engine = Engine::new();
        let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
        let e3024: Vec<_> = issues
            .iter()
            .filter(|i| i.rule_id.as_deref() == Some("E3024"))
            .collect();
        // Without a schema provider, E3024 can't determine taggability — no errors expected
        assert!(e3024.is_empty());
    }
}

crate::register_cfn_lint_rule!(E3024);
