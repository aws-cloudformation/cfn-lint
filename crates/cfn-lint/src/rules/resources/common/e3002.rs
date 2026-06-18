use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E3002;

impl CfnLintRule for E3002 {
    fn id(&self) -> &str {
        "E3002"
    }

    fn short_description(&self) -> &str {
        "Resource properties are invalid"
    }

    fn description(&self) -> &str {
        "Validates resource properties against CloudFormation schema"
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

crate::register_cfn_lint_rule!(E3002);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use indexmap::IndexMap;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3002.id(), "E3002");
        assert_eq!(E3002.short_description(), "Resource properties are invalid");
        assert_eq!(E3002.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E3002.validate_template(&tmpl, &root).is_empty());
    }
}
