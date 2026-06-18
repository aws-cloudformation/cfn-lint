use std::collections::{HashMap, HashSet};

use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct E3004;

impl CfnLintRule for E3004 {
    fn id(&self) -> &str { "E3004" }
    fn short_description(&self) -> &str { "Resource dependencies are not circular" }
    fn description(&self) -> &str { "Check for circular dependencies between resources" }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let resource_names: HashSet<&str> = template.resources.keys().map(|s| s.as_str()).collect();
        let resources_node = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(o) => o,
            None => return vec![],
        };

        // Build dependency graph: resource -> set of resources it depends on
        let mut graph: HashMap<&str, HashSet<String>> = HashMap::new();
        for (name, resource) in &template.resources {
            let mut deps: HashSet<String> = resource.depends_on.iter().cloned().collect();
            // Collect implicit deps from Ref, GetAtt, Sub within this resource's properties
            if let Some(res_node) = resources_node.get(name.as_str()) {
                collect_resource_refs(res_node, &resource_names, &mut deps);
            }
            graph.insert(name.as_str(), deps);
        }

        // Find cycles - report one error per resource in a cycle
        let mut issues = Vec::new();
        let mut reported: HashSet<String> = HashSet::new();

        for name in template.resources.keys() {
            let mut visited = HashSet::new();
            let mut stack = Vec::new();
            let cycle = find_cycle(name.as_str(), &graph, &mut visited, &mut stack);
            if let Some(cycle) = cycle {
                for res in &cycle {
                    if reported.contains(res) { continue; }
                    reported.insert(res.clone());
                    // Find what it cycles with
                    let deps: Vec<&str> = graph.get(res.as_str())
                        .map(|d| d.iter()
                            .filter(|dep| cycle.contains(dep))
                            .map(|s| s.as_str())
                            .collect())
                        .unwrap_or_default();
                    let pos = resources_node.get(res.as_str())
                        .map(|n| n.span().clone())
                        .unwrap_or_default();
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "Circular Dependencies for resource {}. Circular dependency with {:?}",
                            res, deps
                        ),
                        path: vec!["Resources".into(), res.clone()],
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
        issues
    }
}

fn collect_resource_refs(node: &AstNode, resources: &HashSet<&str>, deps: &mut HashSet<String>) {
    ast::walk(node, &[], &mut |n, _| {
        if let AstNode::Function(func) = n {
            match func.name.as_str() {
                "Ref" => {
                    if let Some(name) = func.args.as_str() {
                        if resources.contains(name) {
                            deps.insert(name.to_string());
                        }
                    }
                }
                "Fn::GetAtt" => {
                    let res_name = if let Some(s) = func.args.as_str() {
                        s.split('.').next().map(|s| s.to_string())
                    } else if let Some(arr) = func.args.as_array() {
                        arr.elements.first().and_then(|e| e.as_str()).map(|s| s.to_string())
                    } else { None };
                    if let Some(name) = res_name {
                        if resources.contains(name.as_str()) {
                            deps.insert(name);
                        }
                    }
                }
                "Fn::Sub" => {
                    let template_str = if let Some(s) = func.args.as_str() {
                        Some(s.to_string())
                    } else if let Some(arr) = func.args.as_array() {
                        arr.elements.first().and_then(|e| e.as_str()).map(|s| s.to_string())
                    } else { None };
                    if let Some(s) = template_str {
                        for cap in s.split("${").skip(1) {
                            if let Some(var) = cap.split('}').next() {
                                let name = var.split('.').next().unwrap_or(var);
                                if resources.contains(name) {
                                    deps.insert(name.to_string());
                                }
                            }
                        }
                    }
                }
                _ => {}
            }
        }
        true
    });
}

fn find_cycle<'a>(
    start: &'a str,
    graph: &'a HashMap<&'a str, HashSet<String>>,
    visited: &mut HashSet<&'a str>,
    stack: &mut Vec<&'a str>,
) -> Option<Vec<String>> {
    visited.insert(start);
    stack.push(start);

    if let Some(deps) = graph.get(start) {
        for dep in deps {
            if let Some(&dep_ref) = graph.keys().find(|k| **k == dep.as_str()) {
                if !visited.contains(dep_ref) {
                    if let Some(cycle) = find_cycle(dep_ref, graph, visited, stack) {
                        return Some(cycle);
                    }
                } else if stack.contains(&dep_ref) {
                    let idx = stack.iter().position(|&n| n == dep_ref).unwrap();
                    return Some(stack[idx..].iter().map(|s| s.to_string()).collect());
                }
            }
        }
    }

    stack.pop();
    None
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_no_cycle() {
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    DependsOn: B
  B:
    Type: AWS::SNS::Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3004.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_direct_cycle() {
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    DependsOn: B
  B:
    Type: AWS::SNS::Topic
    DependsOn: A
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 2);
    }

    #[test]
    fn test_self_ref() {
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    DependsOn: A
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_implicit_ref_cycle() {
        let yaml = br#"
Resources:
  A:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Ref B
  B:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Ref A
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 2);
    }
}

crate::register_cfn_lint_rule!(E3004);
