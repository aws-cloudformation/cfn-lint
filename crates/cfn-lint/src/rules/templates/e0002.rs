use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E0002: Error processing rule on the template.
///
/// Placeholder rule — rule processing errors are tagged with this ID
/// when a rule itself fails. `validate` is intentionally empty.
pub struct E0002;

impl CfnLintRule for E0002 {
    fn id(&self) -> &str {
        "E0002"
    }

    fn short_description(&self) -> &str {
        "Error processing rule on the template"
    }

    fn description(&self) -> &str {
        "Errors found when processing a rule on the template"
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
        vec![]
    }
}

crate::register_cfn_lint_rule!(E0002);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    fn empty_template() -> (Template, AstNode) {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        (tmpl, root)
    }

    #[test]
    fn test_metadata() {
        assert_eq!(E0002.id(), "E0002");
        assert_eq!(E0002.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let (tmpl, root) = empty_template();
        assert!(E0002.validate_template(&tmpl, &root).is_empty());
    }
}
