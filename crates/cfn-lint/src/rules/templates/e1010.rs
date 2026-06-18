use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1010;

impl CfnLintRule for E1010 {
    fn id(&self) -> &str {
        "E1010"
    }

    fn short_description(&self) -> &str {
        "GetAtt validation of parameters"
    }

    fn description(&self) -> &str {
        "Validates GetAtt function parameters are correct"
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

crate::register_cfn_lint_rule!(E1010);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use indexmap::IndexMap;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E1010.id(), "E1010");
        assert_eq!(E1010.short_description(), "GetAtt validation of parameters");
        assert_eq!(E1010.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1010.validate_template(&tmpl, &root).is_empty());
    }
}
