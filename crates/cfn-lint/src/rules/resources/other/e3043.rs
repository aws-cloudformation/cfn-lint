use std::collections::{HashMap, HashSet};
use std::path::Path;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3043: Validate parameters for a nested stack.
pub struct E3043;

impl CfnLintRule for E3043 {
    fn id(&self) -> &str {
        "E3043"
    }
    fn short_description(&self) -> &str {
        "Validate parameters for in a nested stack"
    }
    fn description(&self) -> &str {
        "Evaluate if parameters for a nested stack are specified and \
         if parameters are specified for a nested stack that aren't required"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let base_dir = match template
            .filename
            .as_ref()
            .and_then(|f| Path::new(f).parent().map(|p| p.to_path_buf()))
        {
            Some(d) => d,
            None => return vec![],
        };

        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::CloudFormation::Stack" {
                continue;
            }
            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            let template_url = match props.get("TemplateURL").and_then(|n| n.as_str()) {
                Some(u) => u,
                None => continue,
            };

            if template_url.starts_with("http://")
                || template_url.starts_with("https://")
                || template_url.starts_with("s3://")
            {
                continue;
            }

            let nested_params = match load_nested_parameters(&base_dir, template_url) {
                Some(p) => p,
                None => continue,
            };

            let path = vec![
                "Resources".to_string(),
                name.to_string(),
                "Properties".to_string(),
                "Parameters".to_string(),
            ];

            let params_node = props.get("Parameters");

            // Expand Fn::If scenarios in the Parameters node
            let scenarios = match params_node {
                Some(node) => expand_fn_if(node),
                None => vec![(HashMap::new(), HashSet::new())],
            };

            for (scenario, specified_params) in &scenarios {
                let is_conditional = !scenario.is_empty();
                compare_params(
                    self,
                    specified_params,
                    &nested_params,
                    if is_conditional { Some(scenario) } else { None },
                    &path,
                    props,
                    &mut issues,
                );
            }
        }
        issues
    }
}

/// Compare specified params vs nested template params and emit issues.
fn compare_params(
    rule: &E3043,
    specified: &HashSet<String>,
    nested: &HashMap<String, bool>,
    scenario: Option<&HashMap<String, bool>>,
    path: &[String],
    props: &AstNode,
    issues: &mut Vec<ValidationError>,
) {
    let nested_keys: HashSet<String> = nested.keys().cloned().collect();

    // Extra parameters not in nested template
    for key in specified.difference(&nested_keys) {
        let (message, issue_path) = match scenario {
            None => (
                format!(
                    "Specified parameter \"{}\" doesn't exist in nested stack template at {}",
                    key,
                    [path, std::slice::from_ref(key)].concat().join("/"),
                ),
                [path, std::slice::from_ref(key)].concat(),
            ),
            Some(sc) => (
                format!(
                    "Specified parameter \"{}\" doesn't exist in nested stack template {}",
                    key,
                    scenario_text(sc),
                ),
                path.to_vec(),
            ),
        };
        issues.push(ValidationError {
            rule_id: Some(rule.id().to_string()),
            message,
            path: issue_path,
            span: match scenario {
                None => props
                    .get("Parameters")
                    .and_then(|p| p.get(key))
                    .map(|n| n.span())
                    .unwrap_or_default(),
                Some(_) => props
                    .get("Parameters")
                    .map(|n| n.span())
                    .unwrap_or_default(),
            },
            keyword: String::new(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        });
    }

    // Required parameters missing from specification
    for (key, has_default) in nested {
        if !has_default && !specified.contains(key) {
            let message = match scenario {
                None => format!(
                    "Nested stack template parameter \"{}\" is not specified at {}",
                    key,
                    path.join("/"),
                ),
                Some(sc) => format!(
                    "Nested stack template parameter \"{}\" is not specified {}",
                    key,
                    scenario_text(sc),
                ),
            };
            issues.push(ValidationError {
                rule_id: Some(rule.id().to_string()),
                message,
                path: path.to_vec(),
                span: props
                    .get("Parameters")
                    .map(|n| n.span())
                    .unwrap_or_default(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
    }
}

/// Format scenario conditions as text matching Python's output.
fn scenario_text(scenario: &HashMap<String, bool>) -> String {
    let mut parts: Vec<String> = scenario
        .iter()
        .map(|(k, v)| {
            format!(
                "when condition \"{}\" is {}",
                k,
                if *v { "True" } else { "False" }
            )
        })
        .collect();
    parts.sort();
    parts.join(" and ")
}

/// Expand Fn::If nodes in a Parameters value into leaf scenarios.
/// Returns vec of (scenario conditions, parameter key set).
///
/// Each leaf carries only the conditions encountered on the path from the
/// root to that leaf (C68). Previously every leaf was backfilled with all
/// globally collected conditions set to `false`, which produced misleading
/// "when condition X is False" messages for conditions unrelated to the leaf.
fn expand_fn_if(node: &AstNode) -> Vec<(HashMap<String, bool>, HashSet<String>)> {
    let mut results = Vec::new();
    expand_fn_if_inner(node, &HashMap::new(), &mut results);
    results
}

/// Recursively expand Fn::If into leaf scenarios.
fn expand_fn_if_inner(
    node: &AstNode,
    current_scenario: &HashMap<String, bool>,
    results: &mut Vec<(HashMap<String, bool>, HashSet<String>)>,
) {
    match node {
        AstNode::Function(func) if func.name == "Fn::If" => {
            if let Some(arr) = func.args.as_array() {
                if arr.elements.len() == 3 {
                    if let Some(cond_name) = arr.elements[0].as_str() {
                        // True branch
                        let mut true_scenario = current_scenario.clone();
                        true_scenario.insert(cond_name.to_string(), true);
                        expand_fn_if_inner(&arr.elements[1], &true_scenario, results);

                        // False branch
                        let mut false_scenario = current_scenario.clone();
                        false_scenario.insert(cond_name.to_string(), false);
                        expand_fn_if_inner(&arr.elements[2], &false_scenario, results);
                    }
                }
            }
        }
        AstNode::Object(obj) => {
            // Leaf: carry only the conditions on the path to this leaf.
            let keys: HashSet<String> = obj.keys().map(|s| s.to_string()).collect();
            results.push((current_scenario.clone(), keys));
        }
        _ => {
            // Non-object, non-Fn::If — treat as empty params.
            results.push((current_scenario.clone(), HashSet::new()));
        }
    }
}

/// Load nested template and return parameter name -> has_default map.
fn load_nested_parameters(base_dir: &Path, template_url: &str) -> Option<HashMap<String, bool>> {
    let nested_path = base_dir.join(template_url);
    let nested_path = nested_path.canonicalize().ok().unwrap_or(nested_path);
    let content = std::fs::read_to_string(&nested_path).ok()?;
    let ast = crate::parser::parse(content.as_bytes()).ok()?;
    let params_node = ast.get("Parameters")?;
    let params_obj = params_node.as_object()?;

    let mut result = HashMap::new();
    for (name, node) in params_obj.iter() {
        let has_default = node.get("Default").is_some();
        result.insert(name.to_string(), has_default);
    }
    Some(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_nested_stack_with_url_skipped() {
        let yaml = br#"
Resources:
  Stack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/mytemplate.yaml
      Parameters:
        Env: prod
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3043.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_nested_stack_non_stack_resource_ignored() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: test
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3043.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_no_filename_returns_empty() {
        let yaml = br#"
Resources:
  Stack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: ./nested.yaml
      Parameters:
        One: a
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        // No filename set, should return empty
        assert!(E3043.validate_template(&tmpl, &ast).is_empty());
    }

    // C68: each leaf scenario must carry only the conditions on its own path,
    // not every condition found anywhere in the tree.
    #[test]
    fn test_expand_fn_if_only_carries_ancestor_conditions() {
        let yaml = br#"
Root:
  Fn::If:
    - CondA
    - Key1: v
    - Fn::If:
        - CondB
        - Key2: v
        - Key3: v
"#;
        let ast = parser::parse(yaml).unwrap();
        let node = ast.get("Root").unwrap();
        let scenarios = expand_fn_if(node);
        assert_eq!(scenarios.len(), 3, "got: {:?}", scenarios);

        // The CondA=true leaf must NOT mention CondB.
        let cond_a_true = scenarios
            .iter()
            .find(|(sc, keys)| keys.contains("Key1") && sc.get("CondA") == Some(&true))
            .expect("missing CondA=true leaf");
        assert_eq!(
            cond_a_true.0.len(),
            1,
            "should only carry CondA: {:?}",
            cond_a_true.0
        );
        assert!(!cond_a_true.0.contains_key("CondB"));

        // The deep leaves carry both CondA and CondB.
        let deep = scenarios
            .iter()
            .find(|(_, keys)| keys.contains("Key2"))
            .expect("missing Key2 leaf");
        assert_eq!(deep.0.get("CondA"), Some(&false));
        assert_eq!(deep.0.get("CondB"), Some(&true));
    }
}

crate::register_cfn_lint_rule!(E3043);
