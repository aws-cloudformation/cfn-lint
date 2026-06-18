/// E1101 — Validate an item against additional checks.
///
/// Anchor/parent rule for cfnLint keyword-driven validation. In Python cfn-lint,
/// this dispatches to child rules based on schema `cfn-lint` keywords. The actual
/// validation is handled by the schema validator infrastructure.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1101;

impl CfnLintRule for E1101 {
    fn id(&self) -> &str {
        "E1101"
    }

    fn short_description(&self) -> &str {
        "Validate an item against additional checks"
    }

    fn description(&self) -> &str {
        "Use supplemental logic to validate properties against cfn-lint keywords"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Dispatched by schema validator to child rules via cfn-lint keywords
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1101);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1101_metadata() {
        assert_eq!(E1101.id(), "E1101");
        assert_eq!(E1101.severity(), Severity::Error);
    }

    #[test]
    fn test_e1101_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default()  });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1101.validate_template(&tmpl, &root).is_empty());
    }
}
