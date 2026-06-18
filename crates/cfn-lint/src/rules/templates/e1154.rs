/// E1154 — Subnet ID format validation.
/// Anchor rule: pattern `^subnet-(([0-9A-Fa-f]{8})|([0-9A-Fa-f]{17}))$` is enforced by
/// `validate_format` in `jsonschema/keywords.rs` for format `AWS::EC2::Subnet::Id`.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1154;

impl CfnLintRule for E1154 {
    fn id(&self) -> &str {
        "E1154"
    }

    fn short_description(&self) -> &str {
        "Validate VPC subnet id format"
    }

    fn description(&self) -> &str {
        "Check that a VPC subnet id matches a pattern"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by jsonschema/keywords.rs validate_format for AWS::EC2::Subnet::Id
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1154);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1154_metadata() {
        assert_eq!(E1154.id(), "E1154");
        assert_eq!(E1154.severity(), Severity::Error);
    }

    #[test]
    fn test_e1154_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1154.validate_template(&tmpl, &root).is_empty());
    }
}
