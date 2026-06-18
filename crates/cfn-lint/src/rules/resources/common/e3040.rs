/// E3040 — Validate we aren't configuring read-only properties.
///
/// Anchor rule. The actual validation is performed by
/// `Engine::validate_readonly_properties`, which checks the
/// `readOnlyProperties` array in each resource's provider schema and
/// reports E3040 if any matching property path is found in the template.
/// This requires schema access that the Rule trait does not provide.
///
/// This rule struct exists solely to provide metadata for `--list-rules`.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3040;

impl CfnLintRule for E3040 {
    fn id(&self) -> &str {
        "E3040"
    }

    fn short_description(&self) -> &str {
        "Validate we aren't configuring read only properties"
    }

    fn description(&self) -> &str {
        "Validate we aren't configuring read-only properties"
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
        // Handled by Engine::validate_readonly_properties
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3040);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3040.id(), "E3040");
        assert_eq!(E3040.severity(), Severity::Error);
        assert!(E3040.description().contains("read-only"));
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let ast = crate::parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3040.validate_template(&tmpl, &ast).is_empty());
    }
}
