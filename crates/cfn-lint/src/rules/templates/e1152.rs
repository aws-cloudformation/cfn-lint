/// E1152 — AMI ID format validation.
/// Anchor rule: pattern `^ami-([0-9a-z]{8}|[0-9a-z]{17})$` is enforced by
/// `validate_format` in `jsonschema/keywords.rs` for format `AWS::EC2::Image::Id`.
/// Note: Python version also allows `resolve:ssm` prefix for LaunchTemplate ImageId paths.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1152;

impl CfnLintRule for E1152 {
    fn id(&self) -> &str {
        "E1152"
    }

    fn short_description(&self) -> &str {
        "Validate AMI id format"
    }

    fn description(&self) -> &str {
        "Check that an AMI id matches a pattern"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by jsonschema/keywords.rs validate_format for AWS::EC2::Image::Id
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1152);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1152_metadata() {
        assert_eq!(E1152.id(), "E1152");
        assert_eq!(E1152.severity(), Severity::Error);
    }

    #[test]
    fn test_e1152_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1152.validate_template(&tmpl, &root).is_empty());
    }
}
