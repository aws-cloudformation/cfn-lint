use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E0000: Parsing error found when parsing the template.
///
/// Placeholder rule — parse errors are emitted by the parser itself and
/// tagged with this rule ID. The `validate` method is intentionally empty.
pub struct E0000;

impl CfnLintRule for E0000 {
    fn id(&self) -> &str {
        "E0000"
    }

    fn short_description(&self) -> &str {
        "Parsing error found when parsing the template"
    }

    fn description(&self) -> &str {
        "Checks for JSON/YAML formatting errors in your template"
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

crate::register_cfn_lint_rule!(E0000);

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
        assert_eq!(E0000.id(), "E0000");
        assert_eq!(E0000.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let (tmpl, root) = empty_template();
        assert!(E0000.validate_template(&tmpl, &root).is_empty());
    }
}
