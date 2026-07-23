use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// E3014: Validate only one of a set of required properties are specified.
///
/// Schema-driven anchor. The actual `requiredXor` keyword validation is
/// handled by the schema validator.
pub struct E3014;

impl CfnLintRule for E3014 {
    fn id(&self) -> &str {
        "E3014"
    }

    fn short_description(&self) -> &str {
        "Validate only one of a set of required properties are specified"
    }

    fn description(&self) -> &str {
        "Validate only one of a set of required properties are specified"
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

crate::register_cfn_lint_rule!(E3014);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Span};

    #[test]
    fn test_metadata() {
        assert_eq!(E3014.id(), "E3014");
        assert_eq!(E3014.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3014.validate_template(&tmpl, &root).is_empty());
    }
}
