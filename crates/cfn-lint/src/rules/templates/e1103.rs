/// E1103 — Parent rule for format validation.
///
/// This is an anchor rule: actual format checking is performed by
/// `validate_format` in `jsonschema/keywords.rs`, which is registered as the
/// handler for the `format` JSON Schema keyword. Child format rules
/// (E1150–E1156) are also anchors that map to specific format strings.
///
/// This rule struct exists solely to provide metadata for `--list-rules`.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1103;

impl CfnLintRule for E1103 {
    fn id(&self) -> &str {
        "E1103"
    }

    fn short_description(&self) -> &str {
        "Validate the format of a value"
    }

    fn description(&self) -> &str {
        "Parent rule for validating the format keyword in schemas"
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
        // Format validation handled by jsonschema/keywords.rs validate_format
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1103);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Position, Span};
    use indexmap::IndexMap;

    #[test]
    fn test_e1103_metadata() {
        assert_eq!(E1103.id(), "E1103");
        assert_eq!(E1103.severity(), Severity::Error);
    }

    #[test]
    fn test_e1103_returns_empty() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1103.validate_template(&tmpl, &root).is_empty());
    }
}
