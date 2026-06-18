/// E1700 — Rules have the appropriate configuration.
///
/// Anchor/parent rule for validating the Rules section structure. In Python cfn-lint,
/// this loads a JSON schema for the Rules section and validates against it. The actual
/// schema-driven validation is handled by the schema validator.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1700;

impl CfnLintRule for E1700 {
    fn id(&self) -> &str {
        "E1700"
    }

    fn short_description(&self) -> &str {
        "Rules have the appropriate configuration"
    }

    fn description(&self) -> &str {
        "Making sure the Rules section is properly configured"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Schema-driven: Rules section structure validated by schema validator
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1700);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1700_metadata() {
        assert_eq!(E1700.id(), "E1700");
        assert_eq!(E1700.severity(), Severity::Error);
    }

    #[test]
    fn test_e1700_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default()  });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1700.validate_template(&tmpl, &root).is_empty());
    }
}
