use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3007: Resources and Parameters must have unique names.
///
/// Mirrors Python cfn-lint `resources/UniqueNames.py`. If a resource logical
/// ID also appears as a parameter name, emit an error on the resource.
pub struct E3007;

impl CfnLintRule for E3007 {
    fn id(&self) -> &str {
        "E3007"
    }

    fn short_description(&self) -> &str {
        "Unique resource and parameter names"
    }

    fn description(&self) -> &str {
        "All resources and parameters must have unique names"
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
        let mut issues = Vec::new();
        let resources_node = root.get("Resources").and_then(|n| n.as_object());

        for resource_name in template.resources.keys() {
            if template.parameters.contains_key(resource_name) {
                let pos = resources_node
                    .and_then(|r| r.get(resource_name))
                    .map(|n| n.span().clone())
                    .unwrap_or_default();
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "Resources and Parameters must not share name: {}",
                        resource_name
                    ),
                    path: vec!["Resources".to_string(), resource_name.clone()],
                    span: pos,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
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
    fn test_no_overlap() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3007.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_overlapping_names() {
        let yaml = br#"
Parameters:
  MyResource:
    Type: String
Resources:
  MyResource:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3007.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3007"));
        assert!(issues[0].message.contains("MyResource"));
        assert_eq!(issues[0].path, vec!["Resources", "MyResource"]);
    }
}

crate::register_cfn_lint_rule!(E3007);
