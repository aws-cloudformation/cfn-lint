use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3005;

impl CfnLintRule for E3005 {
    fn id(&self) -> &str {
        "E3005"
    }

    fn short_description(&self) -> &str {
        "Check DependsOn values for Resources"
    }

    fn description(&self) -> &str {
        "Validates DependsOn references exist and are available given conditions"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/DependsOn", "Resources/*/DependsOn/*"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Only validate string values (individual DependsOn entries)
        let dep_name = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        let mut resource_names: Vec<&str> = ctx.template.resources.keys().map(|s| s.as_str()).collect();

        // Determine the resource that owns this DependsOn by looking at the path
        // Path is like ["Resources", "MyResource", "DependsOn"] or ["Resources", "MyResource", "DependsOn", "0"]
        let owner_resource = if path.len() >= 2 { Some(path[1].as_str()) } else { None };

        // A resource cannot depend on itself
        if let Some(owner) = owner_resource {
            resource_names.retain(|r| *r != owner);
        }

        if !resource_names.contains(&dep_name) {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} is not one of {:?}",
                    dep_name, resource_names
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        // Check conditional availability: if the target resource has a condition
        // and the owner doesn't share that condition, it might not exist.
        let mut errors = Vec::new();
        let target_resource = ctx.template.resources.get(dep_name);
        if let Some(target) = target_resource {
            if let Some(target_condition) = &target.condition {
                // If the owner resource also has the same condition, it's fine
                let owner_condition = owner_resource
                    .and_then(|name| ctx.template.resources.get(name))
                    .and_then(|r| r.condition.as_ref());

                let same_condition = owner_condition
                    .map(|c| c == target_condition)
                    .unwrap_or(false);

                if !same_condition {
                    // Check if the condition being false is satisfiable
                    if ctx.is_condition_satisfiable(target_condition, false) {
                        errors.push(ValidationError {
                rule_id: None,
                            keyword: format!("cfnLint:{}", self.id()),
                            message: format!(
                                "{:?} will not exist when condition {:?} is false",
                                dep_name, target_condition
                            ),
                            path: path.to_vec(),
                            span: instance.span(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }
            }
        }

        errors
    }
}

crate::register_cfn_lint_rule!(E3005);
