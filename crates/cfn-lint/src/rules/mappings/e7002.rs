use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E7002: Mappings are appropriately configured.
///
/// Now handled by the parent schema rule (E7001) via propertyNames.
pub struct E7002;

impl CfnLintRule for E7002 {
    fn id(&self) -> &str {
        "E7002"
    }
    fn short_description(&self) -> &str {
        "Mappings are appropriately configured"
    }
    fn description(&self) -> &str {
        "Check if Mappings are properly configured per CloudFormation limits"
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

crate::register_cfn_lint_rule!(E7002);
