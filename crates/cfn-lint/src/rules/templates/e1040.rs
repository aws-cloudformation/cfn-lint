/// E1040 — Check if GetAtt matches destination format.
///
/// Anchor rule. The actual format comparison for GetAtt return types is
/// performed by `TemplateWalker::validate_function_types`, which resolves GetAtt
/// return types from provider schemas and validates them against the
/// destination property's expected format. Parent rule: E1010.
///
/// This rule struct exists solely to provide metadata for `--list-rules`.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1040;

impl CfnLintRule for E1040 {
    fn id(&self) -> &str {
        "E1040"
    }

    fn short_description(&self) -> &str {
        "Check if GetAtt matches destination format"
    }

    fn description(&self) -> &str {
        "Validate that if source and destination format exists that they match in a GetAtt"
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
        // Handled by TemplateWalker::validate_function_types
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1040);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1040_metadata() {
        assert_eq!(E1040.id(), "E1040");
        assert_eq!(E1040.severity(), Severity::Error);
    }

    #[test]
    fn test_e1040_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1040.validate_template(&tmpl, &root).is_empty());
    }
}
