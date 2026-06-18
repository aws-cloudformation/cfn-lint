/// E1155 — CloudWatch Log Group Name format validation.
/// Anchor rule: pattern `^[\.\-_\/#A-Za-z0-9]{1,512}$` is enforced by
/// `validate_format` in `jsonschema/keywords.rs` for format `AWS::Logs::LogGroup::Name`.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1155;

impl CfnLintRule for E1155 {
    fn id(&self) -> &str {
        "E1155"
    }

    fn short_description(&self) -> &str {
        "Validate CloudWatch logs group name"
    }

    fn description(&self) -> &str {
        "Check that a CloudWatch log group name matches a pattern"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by jsonschema/keywords.rs validate_format for AWS::Logs::LogGroup::Name
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1155);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1155_metadata() {
        assert_eq!(E1155.id(), "E1155");
        assert_eq!(E1155.severity(), Severity::Error);
    }

    #[test]
    fn test_e1155_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1155.validate_template(&tmpl, &root).is_empty());
    }
}
