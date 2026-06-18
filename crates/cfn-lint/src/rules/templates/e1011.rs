/// E1011 — FindInMap validation of configuration.
/// In Python cfn-lint, this is the schema-level validator for Fn::FindInMap that checks
/// output type compatibility and validates the function arguments against the function schema.
/// In our Rust implementation, structural validation is handled by E1028 and schema validation
/// by the schema validator. This rule exists as an anchor for rule ID compatibility.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1011;

impl CfnLintRule for E1011 {
    fn id(&self) -> &str {
        "E1011"
    }

    fn short_description(&self) -> &str {
        "FindInMap validation of configuration"
    }

    fn description(&self) -> &str {
        "Making sure the FindInMap function is a list of appropriate config"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Structural validation handled by E1028; schema validation by schema validator
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1011);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1011_metadata() {
        assert_eq!(E1011.id(), "E1011");
        assert_eq!(E1011.severity(), Severity::Error);
    }

    #[test]
    fn test_e1011_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1011.validate_template(&tmpl, &root).is_empty());
    }
}
