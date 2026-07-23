/// E1022 — Join validation of parameters.
/// In Python cfn-lint, this is the schema-level validator for Fn::Join that checks
/// output type compatibility and validates the function arguments against the function schema.
/// In our Rust implementation, structural validation is handled by E1020 and schema validation
/// by the schema validator. This rule exists as an anchor for rule ID compatibility.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1022;

impl CfnLintRule for E1022 {
    fn id(&self) -> &str {
        "E1022"
    }

    fn short_description(&self) -> &str {
        "Join validation of parameters"
    }

    fn description(&self) -> &str {
        "Making sure the join function is properly configured"
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
        // Structural validation handled by E1020; schema validation by schema validator
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1022);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Span};

    #[test]
    fn test_e1022_metadata() {
        assert_eq!(E1022.id(), "E1022");
        assert_eq!(E1022.severity(), Severity::Error);
    }

    #[test]
    fn test_e1022_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1022.validate_template(&tmpl, &root).is_empty());
    }
}
