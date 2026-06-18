use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static GLOBALS_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/other/sam/globals.json"))
        .unwrap_or_default()
});

const TRANSFORM_SAM: &str = "AWS::Serverless-2016-10-31";

pub struct E3722;

impl CfnLintRule for E3722 {
    fn id(&self) -> &str { "E3722" }
    fn short_description(&self) -> &str { "Validate Globals section" }
    fn description(&self) -> &str {
        "The Globals section is only valid in SAM templates. \
         Check that the Serverless transform is declared and \
         validate the Globals section structure."
    }
    fn severity(&self) -> Severity { Severity::Error }
    fn keywords(&self) -> &[&str] { &["Globals"] }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let globals = match root.get("Globals") {
            Some(n) => n,
            None => return vec![],
        };

        // Check SAM transform is present
        let has_sam_transform = root.get("Transform")
            .map(|t| {
                if let Some(s) = t.as_str() {
                    s == TRANSFORM_SAM
                } else if let Some(arr) = t.as_array() {
                    arr.elements.iter().any(|e| e.as_str() == Some(TRANSFORM_SAM))
                } else {
                    false
                }
            })
            .unwrap_or(false);

        if !has_sam_transform {
            return vec![ValidationError {
                rule_id: Some("E3722".to_string()),
                message: format!(
                    "'Globals' section requires the serverless transform {:?}",
                    TRANSFORM_SAM
                ),
                path: vec!["Globals".to_string()],
                span: globals.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
}];
        }

        // Validate Globals structure against the schema
        let validator = crate::jsonschema::Validator::new(GLOBALS_SCHEMA.clone());
        let path = vec!["Globals".to_string()];
        validator.validate(globals, &GLOBALS_SCHEMA, &path)
            .into_iter()
            .map(|err| ValidationError {
                rule_id: Some("E3722".to_string()),
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

crate::register_cfn_lint_rule!(E3722);
