use std::collections::HashMap;

use crate::ast::AstNode;
use crate::conditions::Conditions;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W1028: Check Fn::If has a path that cannot be reached.
pub struct W1028;

impl CfnLintRule for W1028 {
    fn id(&self) -> &str {
        "W1028"
    }
    fn short_description(&self) -> &str {
        "Check Fn::If has a path that cannot be reached"
    }
    fn description(&self) -> &str {
        "Check Fn::If path can be reached"
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
        if template.conditions.is_empty() {
            return vec![];
        }
        let conditions = Conditions::from_template(template);
        let mut issues = Vec::new();

        let resources = match root.get("Resources").and_then(|r| r.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        for (_name, res_node) in resources.iter() {
            let res_obj = match res_node.as_object() {
                Some(o) => o,
                None => continue,
            };
            // Build initial context from resource-level Condition
            let mut ctx: HashMap<String, bool> = HashMap::new();
            if let Some(cond_node) = res_obj.get("Condition") {
                if let Some(cond_name) = cond_node.as_str() {
                    if template.conditions.contains_key(cond_name) {
                        ctx.insert(cond_name.to_string(), true);
                    }
                }
            }
            // Walk the resource looking for Fn::If
            walk_for_if(res_node, &ctx, &conditions, self, &mut issues);
        }

        issues
    }
}

fn check_if_branch(
    cond_name: &str,
    elements: &[AstNode],
    ctx: &HashMap<String, bool>,
    conditions: &Conditions,
    rule: &W1028,
    issues: &mut Vec<ValidationError>,
) {
    // True branch (index 1)
    let true_unreachable = ctx.get(cond_name) == Some(&false) || {
        let mut true_ctx = ctx.clone();
        true_ctx.insert(cond_name.to_string(), true);
        !conditions.is_condition_set_satisfiable(&true_ctx)
    };
    if true_unreachable {
        issues.push(ValidationError {
            rule_id: Some(rule.id().to_string()),
            message: format!(
                "['Fn::If', 1] is not reachable. When setting condition '{}' to True",
                cond_name
            ),
            path: vec![],
            span: elements[1].span(),
            keyword: String::new(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        });
    } else {
        let mut true_ctx = ctx.clone();
        true_ctx.insert(cond_name.to_string(), true);
        walk_for_if(&elements[1], &true_ctx, conditions, rule, issues);
    }

    // False branch (index 2)
    let false_unreachable = ctx.get(cond_name) == Some(&true) || {
        let mut false_ctx = ctx.clone();
        false_ctx.insert(cond_name.to_string(), false);
        !conditions.is_condition_set_satisfiable(&false_ctx)
    };
    if false_unreachable {
        issues.push(ValidationError {
            rule_id: Some(rule.id().to_string()),
            message: format!(
                "['Fn::If', 2] is not reachable. When setting condition '{}' to False",
                cond_name
            ),
            path: vec![],
            span: elements[2].span(),
            keyword: String::new(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        });
    } else {
        let mut false_ctx = ctx.clone();
        false_ctx.insert(cond_name.to_string(), false);
        walk_for_if(&elements[2], &false_ctx, conditions, rule, issues);
    }
}

fn walk_for_if(
    node: &AstNode,
    ctx: &HashMap<String, bool>,
    conditions: &Conditions,
    rule: &W1028,
    issues: &mut Vec<ValidationError>,
) {
    match node {
        AstNode::Function(func) if func.name == "Fn::If" => {
            if let Some(arr) = func.args.as_array() {
                if arr.elements.len() == 3 {
                    if let Some(cond_name) = arr.elements[0].as_str() {
                        check_if_branch(cond_name, &arr.elements, ctx, conditions, rule, issues);
                    }
                }
            }
        }
        AstNode::Object(obj) => {
            for (_, v) in obj.iter() {
                walk_for_if(v, ctx, conditions, rule, issues);
            }
        }
        AstNode::Array(arr) => {
            for elem in &arr.elements {
                walk_for_if(elem, ctx, conditions, rule, issues);
            }
        }
        AstNode::Function(func) => {
            walk_for_if(&func.args, ctx, conditions, rule, issues);
        }
        _ => {}
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_independent_conditions_both_satisfiable() {
        let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
    pMultiAZ:
        Type: String
        AllowedValues: [true, false]
    pEnhancedMonitoring:
        Type: String
        AllowedValues: [true, false]
Conditions:
    MultiAZ: !Equals [!Ref pMultiAZ, true]
    EnhancedMonitoring: !Equals [!Ref pEnhancedMonitoring, true]
Resources:
    rDB:
        Type: AWS::RDS::DBInstance
        Properties:
            MultiAZ: !If [MultiAZ, true, false]
            MonitoringRoleArn:
              Fn::If:
              - EnhancedMonitoring
              - some-arn
              - !Ref AWS::NoValue
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W1028.validate_template(&tmpl, &ast);
        assert!(
            issues.is_empty(),
            "No W1028 issues expected, got: {:?}",
            issues.iter().map(|i| &i.message).collect::<Vec<_>>()
        );
    }
}

crate::register_cfn_lint_rule!(W1028);
