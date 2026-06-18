/// E1150 — Security Group ID format validation.
/// Anchor rule: pattern `^sg-([a-fA-F0-9]{8}|[a-fA-F0-9]{17})$` is enforced by
/// `validate_format` in `jsonschema/keywords.rs` for format `AWS::EC2::SecurityGroup::Id`.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1150;

impl CfnLintRule for E1150 {
    fn id(&self) -> &str {
        "E1150"
    }

    fn short_description(&self) -> &str {
        "Validate security group format"
    }

    fn description(&self) -> &str {
        "Security groups must ref/getatt to a security group or match the valid pattern"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by jsonschema/keywords.rs validate_format for AWS::EC2::SecurityGroup::Id
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1150);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1150_metadata() {
        assert_eq!(E1150.id(), "E1150");
        assert_eq!(E1150.severity(), Severity::Error);
    }

    #[test]
    fn test_e1150_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1150.validate_template(&tmpl, &root).is_empty());
    }
}
