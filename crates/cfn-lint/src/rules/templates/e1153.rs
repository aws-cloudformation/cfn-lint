/// E1153 — Security Group Name format validation.
/// Anchor rule: pattern `^[a-zA-Z0-9 ._\-:/()#,@\[\]+=&;\{\}!\$\*]+$` is enforced by
/// `validate_format` in `jsonschema/keywords.rs` for format `AWS::EC2::SecurityGroup::GroupName`.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1153;

impl CfnLintRule for E1153 {
    fn id(&self) -> &str {
        "E1153"
    }

    fn short_description(&self) -> &str {
        "Validate security group name"
    }

    fn description(&self) -> &str {
        "Security group names must match the valid pattern"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by jsonschema/keywords.rs validate_format for AWS::EC2::SecurityGroup::GroupName
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1153);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1153_metadata() {
        assert_eq!(E1153.id(), "E1153");
        assert_eq!(E1153.severity(), Severity::Error);
    }

    #[test]
    fn test_e1153_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1153.validate_template(&tmpl, &root).is_empty());
    }
}
