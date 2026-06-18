/// E1151 — VPC ID format validation.
/// Anchor rule: pattern `^vpc-(([0-9A-Fa-f]{8})|([0-9A-Fa-f]{17}))$` is enforced by
/// `validate_format` in `jsonschema/keywords.rs` for format `AWS::EC2::VPC::Id`.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1151;

impl CfnLintRule for E1151 {
    fn id(&self) -> &str {
        "E1151"
    }

    fn short_description(&self) -> &str {
        "Validate VPC id format"
    }

    fn description(&self) -> &str {
        "Check that a VPC id matches a pattern"
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
        // Handled by jsonschema/keywords.rs validate_format for AWS::EC2::VPC::Id
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1151);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1151_metadata() {
        assert_eq!(E1151.id(), "E1151");
        assert_eq!(E1151.severity(), Severity::Error);
    }

    #[test]
    fn test_e1151_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1151.validate_template(&tmpl, &root).is_empty());
    }
}
