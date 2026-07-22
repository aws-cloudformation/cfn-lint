use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3019: Validate that all resources have unique primary identifiers.
pub struct E3019;

impl CfnLintRule for E3019 {
    fn id(&self) -> &str {
        "E3019"
    }
    fn short_description(&self) -> &str {
        "Validate that all resources have unique primary identifiers"
    }
    fn description(&self) -> &str {
        "Use the primary identifiers in a resource schema to validate that \
         resources inside the template are unique"
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
        // Build negation map: if CondA = !Not [Condition CondB], then CondA negates CondB
        let mut negations: HashMap<String, String> = HashMap::new();
        if let Some(conds) = root.get("Conditions").and_then(|c| c.as_object()) {
            for (name, node) in conds.iter() {
                // Check for Fn::Not [Condition: X] pattern
                if let Some(func) = node.as_function() {
                    if func.name == "Fn::Not" {
                        if let Some(arr) = func.args.as_array() {
                            if arr.elements.len() == 1 {
                                if let Some(inner) = arr.elements[0].as_object() {
                                    if let Some(cond_ref) =
                                        inner.get("Condition").and_then(|v| v.as_str())
                                    {
                                        negations.insert(name.to_string(), cond_ref.to_string());
                                        negations.insert(cond_ref.to_string(), name.to_string());
                                    }
                                }
                                if let Some(inner) = arr.elements[0].as_function() {
                                    if inner.name == "Condition" {
                                        if let Some(cond_ref) = inner.args.as_str() {
                                            negations
                                                .insert(name.to_string(), cond_ref.to_string());
                                            negations
                                                .insert(cond_ref.to_string(), name.to_string());
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Groups resources by type: type name -> [(logical name, properties node, ref/condition)].
        type ResourcesByType<'a> = HashMap<&'a str, Vec<(&'a str, &'a AstNode, Option<&'a str>)>>;
        let mut by_type: ResourcesByType = HashMap::new();
        for (name, resource) in &template.resources {
            let props = root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"));
            if let Some(p) = props {
                by_type.entry(&resource.resource_type).or_default().push((
                    name,
                    p,
                    resource.condition.as_deref(),
                ));
            }
        }

        let mut issues = Vec::new();
        for (resource_type, resources) in &by_type {
            if resources.len() < 2 {
                continue;
            }
            let primary_ids = match get_primary_ids(resource_type) {
                Some(ids) => ids,
                None => continue,
            };

            // Each resource produces a list of conditional ID tuples
            let mut seen: Vec<(&str, Vec<ConditionalTuple>)> = Vec::new();
            for &(name, props, condition) in resources {
                let tuples = resolve_id_values(props, &primary_ids, condition);
                if tuples.is_empty() {
                    continue;
                }
                seen.push((name, tuples));
            }

            for i in 0..seen.len() {
                for j in (i + 1)..seen.len() {
                    let has_conflict = seen[i].1.iter().any(|a| {
                        seen[j].1.iter().any(|b| {
                            a.values == b.values
                                && conditions_compatible(&a.conditions, &b.conditions, &negations)
                        })
                    });
                    if has_conflict {
                        // Find the matching values for the message
                        let id_vals = &seen[i]
                            .1
                            .iter()
                            .find(|a| {
                                seen[j].1.iter().any(|b| {
                                    a.values == b.values
                                        && conditions_compatible(
                                            &a.conditions,
                                            &b.conditions,
                                            &negations,
                                        )
                                })
                            })
                            .unwrap()
                            .values;
                        let id_display: Vec<String> = id_vals
                            .iter()
                            .map(|(k, v)| format!("{}={}", k, v))
                            .collect();
                        for name in [seen[i].0, seen[j].0] {
                            let mut path = vec![
                                "Resources".to_string(),
                                name.to_string(),
                                "Properties".to_string(),
                            ];
                            if primary_ids.len() == 1 {
                                path.push(primary_ids[0].to_string());
                            }
                            let pos = root
                                .get("Resources")
                                .and_then(|r| r.get(name))
                                .and_then(|r| r.get("Properties"))
                                .map(|p| p.span())
                                .unwrap_or_default();
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "Primary identifiers {{{}}} should have unique values across resources '{}' and '{}'",
                                    id_display.join(", "),
                                    seen[i].0,
                                    seen[j].0,
                                ),
                                path,
                                span: pos,
                                keyword: String::new(),
                                unknown: false,
                                resolved_from_ref: false,
                                context: vec![],
                                schema_id: None,
});
                        }
                    }
                }
            }
        }
        issues
    }
}

/// A possible value with the condition constraints under which it exists.
/// Each entry in `conditions` maps condition_name -> required_value (true/false).
#[derive(Clone, Debug)]
struct ConditionalValue {
    value: String,
    conditions: HashMap<String, bool>,
}

#[derive(Clone, Debug)]
struct ConditionalTuple {
    values: Vec<(String, String)>,
    conditions: HashMap<String, bool>,
}

/// Check if two condition maps are compatible (no contradictions).
fn conditions_compatible(
    a: &HashMap<String, bool>,
    b: &HashMap<String, bool>,
    negations: &HashMap<String, String>,
) -> bool {
    // Direct conflict: same condition, opposite values
    for (k, v) in a {
        if let Some(bv) = b.get(k) {
            if v != bv {
                return false;
            }
        }
    }
    // Negation conflict: CondA=true in a, and negation(CondA)=true in b
    for (k, v) in a {
        if let Some(neg) = negations.get(k) {
            if let Some(bv) = b.get(neg) {
                // If a has CondA=true and b has NotCondA=true, they're incompatible
                if *v == *bv {
                    return false;
                }
            }
        }
    }
    true
}

/// Given a Properties node, primary identifier keys, and an optional resource
/// condition, return all possible identifier tuples with their condition constraints.
fn resolve_id_values(
    props: &AstNode,
    primary_ids: &[&str],
    resource_condition: Option<&str>,
) -> Vec<ConditionalTuple> {
    let base_conditions: HashMap<String, bool> = resource_condition
        .map(|c| {
            let mut m = HashMap::new();
            m.insert(c.to_string(), true);
            m
        })
        .unwrap_or_default();

    let prop_objects = expand_props(props, &base_conditions);

    let mut result = Vec::new();
    for (obj, obj_conditions) in &prop_objects {
        let mut per_key: Vec<Vec<ConditionalValue>> = Vec::new();
        let mut complete = true;
        for &id in primary_ids {
            match obj.get(id) {
                Some(node) => {
                    let values = extract_string_values(node, obj_conditions);
                    if values.is_empty() {
                        complete = false;
                        break;
                    }
                    per_key.push(values);
                }
                None => {
                    complete = false;
                    break;
                }
            }
        }
        if !complete {
            continue;
        }
        // Cartesian product (usually just 1 key)
        let mut tuples: Vec<ConditionalTuple> = vec![ConditionalTuple {
            values: vec![],
            conditions: obj_conditions.clone(),
        }];
        for (idx, key_values) in per_key.iter().enumerate() {
            let id = primary_ids[idx];
            let mut new_tuples = Vec::new();
            for tuple in &tuples {
                for cv in key_values {
                    let mut merged = tuple.conditions.clone();
                    let mut compat = true;
                    for (k, v) in &cv.conditions {
                        if let Some(ev) = merged.get(k) {
                            if ev != v {
                                compat = false;
                                break;
                            }
                        } else {
                            merged.insert(k.clone(), *v);
                        }
                    }
                    if !compat {
                        continue;
                    }
                    let mut vals = tuple.values.clone();
                    vals.push((id.to_string(), cv.value.clone()));
                    new_tuples.push(ConditionalTuple {
                        values: vals,
                        conditions: merged,
                    });
                }
            }
            tuples = new_tuples;
        }
        result.extend(tuples);
    }
    result
}

/// Expand a Properties node into possible (object_node, conditions) pairs.
fn expand_props<'a>(
    node: &'a AstNode,
    conditions: &HashMap<String, bool>,
) -> Vec<(&'a AstNode, HashMap<String, bool>)> {
    if let Some(func) = node.as_function() {
        if func.name == "Fn::If" {
            if let Some(arr) = func.args.as_array() {
                if arr.elements.len() == 3 {
                    let cond_name = arr.elements[0].as_str().unwrap_or("");
                    let mut result = Vec::new();
                    for (idx, branch) in arr.elements[1..3].iter().enumerate() {
                        if is_no_value(branch) {
                            continue;
                        }
                        let val = idx == 0; // true branch = index 0
                        let mut branch_conds = conditions.clone();
                        // Check compatibility before adding
                        if let Some(existing) = branch_conds.get(cond_name) {
                            if *existing != val {
                                continue; // contradictory
                            }
                        } else {
                            branch_conds.insert(cond_name.to_string(), val);
                        }
                        result.extend(expand_props(branch, &branch_conds));
                    }
                    return result;
                }
            }
        }
        return vec![];
    }
    if node.as_object().is_some() {
        return vec![(node, conditions.clone())];
    }
    vec![]
}

/// Extract all possible string values from a node with their condition constraints.
fn extract_string_values(
    node: &AstNode,
    base_conditions: &HashMap<String, bool>,
) -> Vec<ConditionalValue> {
    if let Some(s) = node.as_str() {
        return vec![ConditionalValue {
            value: s.to_string(),
            conditions: base_conditions.clone(),
        }];
    }
    if let Some(func) = node.as_function() {
        if func.name == "Fn::If" {
            if let Some(arr) = func.args.as_array() {
                if arr.elements.len() == 3 {
                    let cond_name = arr.elements[0].as_str().unwrap_or("");
                    let mut values = Vec::new();
                    for (idx, branch) in arr.elements[1..3].iter().enumerate() {
                        if is_no_value(branch) {
                            continue;
                        }
                        let val = idx == 0;
                        let mut branch_conds = base_conditions.clone();
                        if let Some(existing) = branch_conds.get(cond_name) {
                            if *existing != val {
                                continue;
                            }
                        } else {
                            branch_conds.insert(cond_name.to_string(), val);
                        }
                        values.extend(extract_string_values(branch, &branch_conds));
                    }
                    return values;
                }
            }
        }
        return vec![];
    }
    vec![]
}

/// Check if a node is Ref AWS::NoValue
fn is_no_value(node: &AstNode) -> bool {
    if let Some(func) = node.as_function() {
        if func.name == "Ref" {
            if let Some(s) = func.args.as_str() {
                return s == "AWS::NoValue";
            }
        }
    }
    false
}

/// Get primary identifier property names for known resource types.
fn get_primary_ids(resource_type: &str) -> Option<Vec<&'static str>> {
    match resource_type {
        "AWS::S3::Bucket" => Some(vec!["BucketName"]),
        "AWS::SQS::Queue" => Some(vec!["QueueName"]),
        "AWS::SNS::Topic" => Some(vec!["TopicName"]),
        "AWS::DynamoDB::Table" => Some(vec!["TableName"]),
        "AWS::Lambda::Function" => Some(vec!["FunctionName"]),
        "AWS::IAM::Role" => Some(vec!["RoleName"]),
        // IAM::Policy primary identifier is /properties/Id (read-only, auto-generated)
        // so we don't check it
        "AWS::IAM::ManagedPolicy" => Some(vec!["ManagedPolicyName"]),
        "AWS::ECS::Cluster" => Some(vec!["ClusterName"]),
        "AWS::ECR::Repository" => Some(vec!["RepositoryName"]),
        "AWS::Logs::LogGroup" => Some(vec!["LogGroupName"]),
        "AWS::SSM::Parameter" => Some(vec!["Name"]),
        "AWS::CodeBuild::Project" => Some(vec!["Name"]),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_unique_bucket_names() {
        let yaml = br#"
Resources:
  Bucket1:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket-1
  Bucket2:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket-2
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3019.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_duplicate_bucket_names() {
        let yaml = br#"
Resources:
  Bucket1:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: same-name
  Bucket2:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: same-name
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3019.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 2); // One issue per resource
        assert!(issues.iter().all(|i| i.rule_id.as_deref() == Some("E3019")));
        assert!(issues
            .iter()
            .all(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E')));
    }
}

crate::register_cfn_lint_rule!(E3019);
