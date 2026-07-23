use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3032;

impl CfnLintRule for E3032 {
    fn id(&self) -> &str {
        "E3032"
    }

    fn short_description(&self) -> &str {
        "Check if array has between min and max number of values"
    }

    fn description(&self) -> &str {
        "Validates array properties have the correct number of elements"
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

crate::register_cfn_lint_rule!(E3032);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3032.id(), "E3032");
        assert_eq!(
            E3032.short_description(),
            "Check if array has between min and max number of values"
        );
        assert_eq!(E3032.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3032.validate_template(&tmpl, &root).is_empty());
    }
}
