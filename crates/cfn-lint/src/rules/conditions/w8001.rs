use std::collections::HashSet;

use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W8001 is the warning-level check for unused conditions.
/// It extends E8001 by also checking Output-level Condition fields.
/// Note: E8001 exists as the error-level variant; this rule provides
/// a warning with broader coverage (Output conditions, nested Condition refs).
pub struct W8001;

impl CfnLintRule for W8001 {
    fn id(&self) -> &str {
        "W8001"
    }
    fn short_description(&self) -> &str {
        "Check if Conditions are used"
    }
    fn description(&self) -> &str {
        "Check that conditions defined in the template are referenced somewhere"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // If Conditions exists but is not an object, report E0002 (matches Python behavior
        // where W8001 crashes on non-object Conditions)
        if let Some(conds_node) = root.get("Conditions") {
            if conds_node.as_object().is_none() {
                return vec![ValidationError {
                    rule_id: Some("E0002".to_string()),
                    message: format!(
                        "Unknown exception while processing rule {}: Conditions is not an object",
                        self.id()
                    ),
                    path: vec!["Conditions".to_string()],
                    span: conds_node.span(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }];
            }
        }

        if template.conditions.is_empty() {
            return vec![];
        }

        let mut refs = HashSet::new();

        // Resource Condition fields
        for res in template.resources.values() {
            if let Some(cond) = &res.condition {
                refs.insert(cond.clone());
            }
        }

        // Output Condition fields
        for output_node in template.outputs.values() {
            if let Some(cond_str) = output_node.get("Condition").and_then(|n| n.as_str()) {
                refs.insert(cond_str.to_string());
            }
        }

        // Fn::If and Condition function references throughout the AST
        ast::walk(root, &[], &mut |node, _path| {
            if let AstNode::Function(func) = node {
                match func.name.as_str() {
                    "Fn::If" => {
                        if let Some(arr) = func.args.as_array() {
                            if let Some(name) = arr.elements.first().and_then(|e| e.as_str()) {
                                refs.insert(name.to_string());
                            }
                        }
                    }
                    "Condition" => {
                        if let Some(name) = func.args.as_str() {
                            refs.insert(name.to_string());
                        }
                    }
                    _ => {}
                }
            }
            true
        });

        // Condition references within other conditions (Conditions section)
        if let Some(conds) = root.get("Conditions").and_then(|n| n.as_object()) {
            for (_, cond_node) in conds.iter() {
                collect_condition_refs_in_node(cond_node, &mut refs);
            }
        }

        template
            .conditions
            .keys()
            .filter(|name| !refs.contains(*name))
            .map(|name| ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!("Condition '{}' not used", name),
                path: vec!["Conditions".to_string(), name.clone()],
                span: Default::default(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            })
            .collect()
    }
}

/// Look for "Condition" keys in condition definition objects (e.g., Fn::And/Fn::Or containing Condition refs).
fn collect_condition_refs_in_node(node: &AstNode, refs: &mut HashSet<String>) {
    ast::walk(node, &[], &mut |n, _| {
        if let AstNode::Function(func) = n {
            if func.name == "Condition" {
                if let Some(name) = func.args.as_str() {
                    refs.insert(name.to_string());
                }
            }
        }
        true
    });
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_condition_used_in_output() {
        let yaml = br#"
Conditions:
  IsProd:
    Fn::Equals:
      - a
      - b
Outputs:
  MyOutput:
    Condition: IsProd
    Value: hello
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W8001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_condition_unused() {
        let yaml = br#"
Conditions:
  Unused:
    Fn::Equals:
      - a
      - b
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W8001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("W8001"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("W8001"));
        assert!(issues[0].message.contains("Unused"));
    }
}

crate::register_cfn_lint_rule!(W8001);
