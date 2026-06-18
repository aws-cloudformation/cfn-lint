use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E1702: Validate the configuration of Rules RuleCondition.
///
/// Schema-driven anchor. The actual validation of RuleCondition (must resolve
/// to boolean using condition functions) is handled by the schema validator
/// at path `Rules/*/RuleCondition`.
pub struct E1702;

impl CfnLintRule for E1702 {
    fn id(&self) -> &str {
        "E1702"
    }

    fn short_description(&self) -> &str {
        "Validate the configuration of Rules RuleCondition"
    }

    fn description(&self) -> &str {
        "Make sure the RuleCondition in a Rule is properly configured"
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

crate::register_cfn_lint_rule!(E1702);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_metadata() {
        assert_eq!(E1702.id(), "E1702");
        assert_eq!(E1702.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default()  });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1702.validate_template(&tmpl, &root).is_empty());
    }
}
