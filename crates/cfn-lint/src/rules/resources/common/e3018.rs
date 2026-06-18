use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E3018: Check Properties that need only one of a list of properties.
///
/// Schema-driven anchor. The actual `oneOf` keyword validation is handled
/// by the schema validator.
pub struct E3018;

impl CfnLintRule for E3018 {
    fn id(&self) -> &str {
        "E3018"
    }

    fn short_description(&self) -> &str {
        "Check Properties that need only one of a list of properties"
    }

    fn description(&self) -> &str {
        "Check Properties that need only one of a list of properties"
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

crate::register_cfn_lint_rule!(E3018);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_metadata() {
        assert_eq!(E3018.id(), "E3018");
        assert_eq!(E3018.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default()  });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3018.validate_template(&tmpl, &root).is_empty());
    }
}
