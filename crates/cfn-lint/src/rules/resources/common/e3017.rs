use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3017: Check Properties that need at least one of a list of properties.
///
/// Schema-driven anchor. The actual `anyOf` keyword validation is handled
/// by the schema validator.
pub struct E3017;

impl CfnLintRule for E3017 {
    fn id(&self) -> &str {
        "E3017"
    }

    fn short_description(&self) -> &str {
        "Check Properties that need at least one of a list of properties"
    }

    fn description(&self) -> &str {
        "Check Properties that need at least one of a list of properties"
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

crate::register_cfn_lint_rule!(E3017);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_metadata() {
        assert_eq!(E3017.id(), "E3017");
        assert_eq!(E3017.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3017.validate_template(&tmpl, &root).is_empty());
    }
}
