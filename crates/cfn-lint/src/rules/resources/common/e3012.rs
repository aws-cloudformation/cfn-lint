use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E3012;

impl CfnLintRule for E3012 {
    fn id(&self) -> &str {
        "E3012"
    }

    fn short_description(&self) -> &str {
        "Check resource properties values"
    }

    fn description(&self) -> &str {
        "Validates resource property values against CloudFormation schema"
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

crate::register_cfn_lint_rule!(E3012);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use indexmap::IndexMap;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3012.id(), "E3012");
        assert_eq!(E3012.short_description(), "Check resource properties values");
        assert_eq!(E3012.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3012.validate_template(&tmpl, &root).is_empty());
    }
}
