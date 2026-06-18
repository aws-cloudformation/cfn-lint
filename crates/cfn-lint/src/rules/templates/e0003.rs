use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E0003: Error with cfn-lint configuration.
///
/// Placeholder rule — configuration errors are tagged with this ID.
/// `validate` is intentionally empty.
pub struct E0003;

impl CfnLintRule for E0003 {
    fn id(&self) -> &str {
        "E0003"
    }

    fn short_description(&self) -> &str {
        "Error with cfn-lint configuration"
    }

    fn description(&self) -> &str {
        "Error as a result of the cfn-lint configuration"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E0003);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    fn empty_template() -> (Template, AstNode) {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        (tmpl, root)
    }

    #[test]
    fn test_metadata() {
        assert_eq!(E0003.id(), "E0003");
        assert_eq!(E0003.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let (tmpl, root) = empty_template();
        assert!(E0003.validate_template(&tmpl, &root).is_empty());
    }
}
