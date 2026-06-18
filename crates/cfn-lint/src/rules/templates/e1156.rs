/// E1156 — IAM Role ARN format validation.
/// Anchor rule: pattern `^arn:(aws|aws-cn|aws-iso|aws-iso-[a-z]{1}|aws-us-gov):iam::\d{12}:role/.*$`
/// is enforced by `validate_format` in `jsonschema/keywords.rs` for format `AWS::IAM::Role::Arn`.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1156;

impl CfnLintRule for E1156 {
    fn id(&self) -> &str {
        "E1156"
    }

    fn short_description(&self) -> &str {
        "Validate IAM role ARN format"
    }

    fn description(&self) -> &str {
        "Validate IAM role ARN for ref/getatt and string values"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by jsonschema/keywords.rs validate_format for AWS::IAM::Role::Arn
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1156);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1156_metadata() {
        assert_eq!(E1156.id(), "E1156");
        assert_eq!(E1156.severity(), Severity::Error);
    }

    #[test]
    fn test_e1156_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1156.validate_template(&tmpl, &root).is_empty());
    }
}
