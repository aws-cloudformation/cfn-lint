use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../data/schemas/other/metadata/cfn_lint.json"))
        .unwrap_or_default()
});

/// W4005: Validate cfnlint configuration in the Metadata.
pub struct W4005;

impl CfnLintRule for W4005 {
    fn id(&self) -> &str {
        "W4005"
    }
    fn short_description(&self) -> &str {
        "Validate cfnlint configuration in the Metadata"
    }
    fn description(&self) -> &str {
        "Metadata cfn-lint configuration has many values and we want to \
         validate that they are configured correctly"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }
    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let cfn_lint = match root.get("Metadata").and_then(|m| m.get("cfn-lint")) {
            Some(n) => n,
            None => return vec![],
        };
        let validator = Validator::new(SCHEMA.clone());
        let base_path = vec![
            "Metadata".to_string(),
            "cfn-lint".to_string(),
        ];
        validator
            .validate(cfn_lint, &SCHEMA, &base_path)
            .into_iter()
            .filter(|e| !e.unknown)
            .map(|err| ValidationError {
                rule_id: Some("W4005".to_string()),
                message: err.message,
                path: err.path,
                span: err.span,
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
            schema_id: None,
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(W4005);
