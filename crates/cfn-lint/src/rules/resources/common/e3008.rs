use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E3008: Validate an array in order (prefixItems).
///
/// Schema-driven anchor. The actual `prefixItems` keyword validation is
/// handled by the schema validator.
pub struct E3008;

impl CfnLintRule for E3008 {
    fn id(&self) -> &str {
        "E3008"
    }

    fn short_description(&self) -> &str {
        "Validate an array in order"
    }

    fn description(&self) -> &str {
        "Will validate arrays in order for schema validation"
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

crate::register_cfn_lint_rule!(E3008);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_metadata() {
        assert_eq!(E3008.id(), "E3008");
        assert_eq!(E3008.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default()  });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3008.validate_template(&tmpl, &root).is_empty());
    }
}
