/// E1041 — Check if Ref matches destination format.
///
/// Anchor rule. The actual format comparison for Ref return types is
/// performed by `TemplateWalker::validate_function_types`, which resolves Ref
/// return types from provider schemas and validates them against the
/// destination property's expected format. Parent rule: E1020.
///
/// This rule struct exists solely to provide metadata for `--list-rules`.
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct E1041;

impl CfnLintRule for E1041 {
    fn id(&self) -> &str {
        "E1041"
    }

    fn short_description(&self) -> &str {
        "Check if Ref matches destination format"
    }

    fn description(&self) -> &str {
        "When source and destination format exists validate that they match in a Ref"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Handled by TemplateWalker::validate_function_types
                vec![]
    }
}

crate::register_cfn_lint_rule!(E1041);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1041_metadata() {
        assert_eq!(E1041.id(), "E1041");
        assert_eq!(E1041.severity(), Severity::Error);
    }

    #[test]
    fn test_e1041_returns_empty() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default()  });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1041.validate_template(&tmpl, &root).is_empty());
    }
}
