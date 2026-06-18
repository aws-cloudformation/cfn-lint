/// E1701 — Validate the configuration of Assertions in Rules.
///
/// Anchor/parent rule for validating Assert values within Rules/*/Assertions/*/Assert.
/// In Python cfn-lint, this validates that Assert values resolve to booleans using
/// condition functions. The actual validation is schema-driven.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1701;

impl CfnLintRule for E1701 {
    fn id(&self) -> &str {
        "E1701"
    }

    fn short_description(&self) -> &str {
        "Validate the configuration of Assertions"
    }

    fn description(&self) -> &str {
        "Make sure the Assert value in a Rule is properly configured"
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
        // Schema-driven: Assert structure validated by schema validator
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1701);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1701_metadata() {
        assert_eq!(E1701.id(), "E1701");
        assert_eq!(E1701.severity(), Severity::Error);
    }

    #[test]
    fn test_e1701_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1701.validate_template(&tmpl, &root).is_empty());
    }
}
