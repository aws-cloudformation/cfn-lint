use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct W6001;

impl CfnLintRule for W6001 {
    fn id(&self) -> &str {
        "W6001"
    }
    fn short_description(&self) -> &str {
        "Check Outputs using ImportValue"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<ValidationError> {
        let mut issues = Vec::new();
        let outputs = match root.get("Outputs").and_then(|n| n.as_object()) {
            Some(o) => o,
            None => return issues,
        };

        for (name, output_node) in outputs.iter() {
            if let Some(value) = output_node.get("Value") {
                if has_import_value(value) {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: "The output value is an import from another output".to_string(),
                        path: vec!["Outputs".to_string(), name.to_string(), "Value".to_string()],
                        span: value.span(),
                        ..Default::default()
                    });
                }
            }
        }
        issues
    }
}

fn has_import_value(node: &AstNode) -> bool {
    matches!(node.as_function(), Some(f) if f.name == "Fn::ImportValue")
}

crate::register_cfn_lint_rule!(W6001);
