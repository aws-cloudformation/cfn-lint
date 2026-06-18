//! Resource dependency graph and condition-aware validation.
//!
//! Builds a directed graph of resource relationships (Ref, GetAtt, Sub, DependsOn)
//! and checks whether referenced resources are guaranteed to exist given conditions.

use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

use regex::Regex;

use crate::ast::{self, AstNode};
use crate::template::Template;

static RE_SUB_VARS: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\$\{([^}!]+)\}").unwrap());

/// Type of dependency edge.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EdgeKind {
    Ref,
    GetAtt,
    Sub,
    DependsOn,
}

impl EdgeKind {
    pub fn label(&self) -> &str {
        match self {
            EdgeKind::Ref => "Ref",
            EdgeKind::GetAtt => "GetAtt",
            EdgeKind::Sub => "Sub",
            EdgeKind::DependsOn => "DependsOn",
        }
    }
}

/// An edge from source resource to target resource.
#[derive(Debug, Clone)]
pub struct Edge {
    pub source: String,
    pub target: String,
    pub kind: EdgeKind,
    /// Path segments from the source resource node to where the reference occurs.
    /// e.g. ["Properties", "Parameters", "pVPC"]
    pub source_path: Vec<String>,
}

/// Dependency graph of resources.
pub struct Graph {
    pub edges: Vec<Edge>,
}

impl Graph {
    /// Build the graph from a template and its AST.
    pub fn build(template: &Template, root: &AstNode) -> Self {
        let resources_node = root.get("Resources");
        let mut edges = Vec::new();

        for (name, resource) in &template.resources {
            // DependsOn edges
            for dep in &resource.depends_on {
                if template.resources.contains_key(dep) {
                    edges.push(Edge {
                        source: name.clone(),
                        target: dep.clone(),
                        kind: EdgeKind::DependsOn,
                        source_path: vec!["DependsOn".to_string()],
                    });
                }
            }

            // Ref/GetAtt/Sub edges from walking the resource AST
            if let Some(res_node) = resources_node.as_ref().and_then(|r| r.get(name)) {
                collect_ref_edges(res_node, name, template, &mut edges);
            }
        }

        // Also collect edges from Outputs
        if let Some(outputs_node) = root.get("Outputs") {
            if let Some(obj) = outputs_node.as_object() {
                for (output_name, output_node) in obj.iter() {
                    let source = format!("Output-{}", output_name);
                    collect_ref_edges_with_source(
                        output_node,
                        &source,
                        template,
                        &mut edges,
                        &[],
                    );
                }
            }
        }

        Graph { edges }
    }

    /// Get all edges from a given source resource.
    pub fn edges_from(&self, source: &str) -> Vec<&Edge> {
        self.edges.iter().filter(|e| e.source == source).collect()
    }

    /// Get all non-DependsOn targets for a source (implicit dependencies).
    pub fn implicit_deps(&self, source: &str) -> HashSet<&str> {
        self.edges
            .iter()
            .filter(|e| e.source == source && e.kind != EdgeKind::DependsOn)
            .map(|e| e.target.as_str())
            .collect()
    }
}

/// Walk a resource node collecting Ref/GetAtt/Sub edges.
fn collect_ref_edges(
    res_node: &AstNode,
    resource_name: &str,
    template: &Template,
    edges: &mut Vec<Edge>,
) {
    collect_ref_edges_with_source(res_node, resource_name, template, edges, &[]);
}

fn collect_ref_edges_with_source(
    node: &AstNode,
    source: &str,
    template: &Template,
    edges: &mut Vec<Edge>,
    base_path: &[String],
) {
    ast::walk(node, base_path, &mut |n, path| {
        if let AstNode::Function(func) = n {
            match func.name.as_str() {
                "Ref" => {
                    if let Some(target) = func.args.as_str() {
                        if template.resources.contains_key(target) {
                            edges.push(Edge {
                                source: source.to_string(),
                                target: target.to_string(),
                                kind: EdgeKind::Ref,
                                source_path: path.to_vec(),
                            });
                        }
                    }
                }
                "Fn::GetAtt" => {
                    let target = if let Some(arr) = func.args.as_array() {
                        arr.elements.first().and_then(|e| e.as_str())
                    } else if let Some(s) = func.args.as_str() {
                        s.split('.').next()
                    } else {
                        None
                    };
                    if let Some(target) = target {
                        if template.resources.contains_key(target) {
                            edges.push(Edge {
                                source: source.to_string(),
                                target: target.to_string(),
                                kind: EdgeKind::GetAtt,
                                source_path: path.to_vec(),
                            });
                        }
                    }
                }
                "Fn::Sub" => {
                    let sub_str = if let Some(s) = func.args.as_str() {
                        Some(s.to_string())
                    } else if let Some(arr) = func.args.as_array() {
                        arr.elements.first().and_then(|e| e.as_str()).map(|s| s.to_string())
                    } else {
                        None
                    };
                    if let Some(s) = sub_str {
                        for cap in RE_SUB_VARS.captures_iter(&s) {
                            let var = &cap[1];
                            let name = var.split('.').next().unwrap_or(var);
                            if template.resources.contains_key(name) {
                                edges.push(Edge {
                                    source: source.to_string(),
                                    target: name.to_string(),
                                    kind: EdgeKind::Sub,
                                    source_path: path.to_vec(),
                                });
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

/// Collect conditions along a path in the template.
///
/// Returns a map of condition_name → set of bool values indicating whether
/// the condition must be True or False (or both) for this path to be reached.
///
/// Conditions come from:
/// 1. Resource/Output `Condition` property (always True for the resource to exist)
/// 2. `Fn::If` branches along the path (True for then-branch, False for else-branch)
pub fn get_conditions_from_path(
    root: &AstNode,
    path: &[String],
) -> HashMap<String, HashSet<bool>> {
    let mut conditions: HashMap<String, HashSet<bool>> = HashMap::new();

    if path.len() < 2 {
        return conditions;
    }

    // Check resource/output condition
    let section = &path[0];
    let name = &path[1];
    if section == "Resources" || section == "Outputs" {
        if let Some(section_node) = root.get(section) {
            if let Some(item_node) = section_node.get(name) {
                if let Some(cond_node) = item_node.get("Condition") {
                    if let Some(cond_name) = cond_node.as_str() {
                        conditions
                            .entry(cond_name.to_string())
                            .or_default()
                            .insert(true);
                    }
                }
            }
        }
    }

    // Walk the path looking for Fn::If branches
    let mut current = match root.get(section) {
        Some(n) => n,
        None => return conditions,
    };

    let segments = &path[1..];
    let mut i = 0;
    while i < segments.len() {
        // Try navigating: handle Object, Array, and Function (Fn::If) nodes
        let next = if let Some(n) = current.get(&segments[i]) {
            n
        } else if let Some(arr) = current.as_array() {
            if let Ok(idx) = segments[i].parse::<usize>() {
                if let Some(n) = arr.elements.get(idx) {
                    n
                } else {
                    break;
                }
            } else {
                break;
            }
        } else if let Some(func) = current.as_function() {
            // Function node — check if it's Fn::If and navigate into branches
            if func.name == "Fn::If" {
                if let Some(arr) = func.args.as_array() {
                    if arr.elements.len() == 3 {
                        if let Some(cond_name) = arr.elements[0].as_str() {
                            if let Ok(idx) = segments[i].parse::<usize>() {
                                if idx == 1 {
                                    conditions
                                        .entry(cond_name.to_string())
                                        .or_default()
                                        .insert(true);
                                } else if idx == 2 {
                                    conditions
                                        .entry(cond_name.to_string())
                                        .or_default()
                                        .insert(false);
                                }
                                if let Some(n) = arr.elements.get(idx) {
                                    n
                                } else {
                                    break;
                                }
                            } else {
                                break;
                            }
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            } else {
                // Non-If function — try navigating into args
                if let Some(arr) = func.args.as_array() {
                    if let Ok(idx) = segments[i].parse::<usize>() {
                        if let Some(n) = arr.elements.get(idx) {
                            n
                        } else {
                            break;
                        }
                    } else if let Some(obj) = func.args.as_object() {
                        if let Some(n) = obj.get(&segments[i]) {
                            n
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                } else if let Some(obj) = func.args.as_object() {
                    if let Some(n) = obj.get(&segments[i]) {
                        n
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            }
        } else {
            break;
        };

        current = next;
        i += 1;
    }

    conditions
}

/// Check if a target resource is available given the conditions along a source path.
///
/// Returns a list of scenarios where the resource is NOT available.
/// Empty list means the resource is always available from this path.
pub fn is_resource_available(
    template: &Template,
    root: &AstNode,
    source_path: &[String],
    target_resource: &str,
) -> Vec<HashMap<String, bool>> {
    let path_conditions = get_conditions_from_path(root, source_path);

    let resource_condition = template
        .resources
        .get(target_resource)
        .and_then(|r| r.condition.as_deref());

    let resource_condition = match resource_condition {
        Some(c) => c,
        None => return vec![], // No condition = always exists
    };

    // If no path conditions, the source always exists but target is conditional
    if path_conditions.is_empty() {
        let mut scenario = HashMap::new();
        scenario.insert(resource_condition.to_string(), false);
        return vec![scenario];
    }

    // If the resource condition appears in path conditions as True, it's safe
    if let Some(values) = path_conditions.get(resource_condition) {
        if values.contains(&true) {
            return vec![];
        }
        if values.contains(&false) {
            let mut scenario = HashMap::new();
            scenario.insert(resource_condition.to_string(), false);
            return vec![scenario];
        }
    }

    // Check if any path condition implies the resource condition.
    // For simple cases: if the source resource has the same condition, it's safe.
    // For complex cases we'd need a SAT solver. For now, check direct implication
    // through condition definitions.
    let mut scenario: HashMap<String, bool> = HashMap::new();
    for (cond_name, cond_values) in &path_conditions {
        if cond_values.len() > 1 {
            // Both True and False — this condition doesn't constrain
            return vec![];
        }
        let value = match cond_values.iter().next() {
            Some(v) => *v,
            None => continue,
        };
        scenario.insert(cond_name.clone(), value);
    }

    // Check if the scenario implies the resource condition is true.
    if scenario.get(resource_condition) == Some(&true) {
        return vec![];
    }

    // Use the SAT solver to check if the scenario implies the resource condition
    let conditions = crate::conditions::Conditions::from_template(template);
    if conditions.check_implies(&scenario, resource_condition) {
        return vec![];
    }

    // Resource condition is not implied — return the failure scenario
    let mut result = scenario;
    result.insert(resource_condition.to_string(), false);
    vec![result]
}

/// Check if a set of condition states implies that another condition must be true.
///
/// This handles common patterns:
/// - Same condition name

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    fn parse(yaml: &[u8]) -> (Template, AstNode) {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        (tmpl, ast)
    }

    #[test]
    fn test_graph_ref_edge() {
        let (tmpl, ast) = parse(br#"
Resources:
  Topic:
    Type: AWS::SNS::Topic
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Topic
"#);
        let graph = Graph::build(&tmpl, &ast);
        let edges: Vec<_> = graph.edges.iter().filter(|e| e.kind == EdgeKind::Ref).collect();
        assert_eq!(edges.len(), 1);
        assert_eq!(edges[0].source, "Bucket");
        assert_eq!(edges[0].target, "Topic");
    }

    #[test]
    fn test_graph_getatt_edge() {
        let (tmpl, ast) = parse(br#"
Resources:
  Vpc:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !GetAtt Vpc.VpcId
"#);
        let graph = Graph::build(&tmpl, &ast);
        let edges: Vec<_> = graph.edges.iter().filter(|e| e.kind == EdgeKind::GetAtt).collect();
        assert_eq!(edges.len(), 1);
        assert_eq!(edges[0].source, "Subnet");
        assert_eq!(edges[0].target, "Vpc");
    }

    #[test]
    fn test_resource_available_no_condition() {
        let (tmpl, ast) = parse(br#"
Resources:
  Topic:
    Type: AWS::SNS::Topic
  Bucket:
    Type: AWS::S3::Bucket
"#);
        let path = vec!["Resources".into(), "Bucket".into(), "Properties".into()];
        assert!(is_resource_available(&tmpl, &ast, &path, "Topic").is_empty());
    }

    #[test]
    fn test_resource_unavailable_conditional_target() {
        let (tmpl, ast) = parse(br#"
Conditions:
  CreateTopic:
    Fn::Equals: [a, b]
Resources:
  Topic:
    Type: AWS::SNS::Topic
    Condition: CreateTopic
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Topic
"#);
        let path = vec!["Resources".into(), "Bucket".into(), "Properties".into(), "BucketName".into()];
        let scenarios = is_resource_available(&tmpl, &ast, &path, "Topic");
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].get("CreateTopic"), Some(&false));
    }

    #[test]
    fn test_resource_available_same_condition() {
        let (tmpl, ast) = parse(br#"
Conditions:
  CreateResources:
    Fn::Equals: [a, b]
Resources:
  Topic:
    Type: AWS::SNS::Topic
    Condition: CreateResources
  Bucket:
    Type: AWS::S3::Bucket
    Condition: CreateResources
    Properties:
      BucketName: !Ref Topic
"#);
        let path = vec!["Resources".into(), "Bucket".into(), "Properties".into(), "BucketName".into()];
        assert!(is_resource_available(&tmpl, &ast, &path, "Topic").is_empty());
    }

    #[test]
    fn test_resource_available_and_condition_implies() {
        let (tmpl, ast) = parse(br#"
Conditions:
  BaseEnabled:
    Fn::Equals: [true, a]
  SubEnabled:
    Fn::And:
      - !Condition BaseEnabled
      - Fn::Equals: [true, b]
Resources:
  Queue:
    Type: AWS::SQS::Queue
    Condition: BaseEnabled
  Sub:
    Type: AWS::SNS::Subscription
    Condition: SubEnabled
    Properties:
      Endpoint: !GetAtt Queue.Arn
"#);
        let path = vec!["Resources".into(), "Sub".into(), "Properties".into(), "Endpoint".into()];
        let scenarios = is_resource_available(&tmpl, &ast, &path, "Queue");
        // SubEnabled = And(BaseEnabled, ...) so SubEnabled=true implies BaseEnabled=true
        assert!(scenarios.is_empty(), "Expected no issues but got: {:?}", scenarios);
    }

    #[test]
    fn test_resource_available_and_condition_implies_tag_form() {
        // Uses !And and !Condition tag forms (parsed as Function nodes)
        let (tmpl, ast) = parse(br#"
Conditions:
  BaseEnabled:
    Fn::Equals: [true, a]
  SubEnabled: !And
    - !Condition BaseEnabled
    - !Equals [true, b]
Resources:
  Queue:
    Type: AWS::SQS::Queue
    Condition: BaseEnabled
  Sub:
    Type: AWS::SNS::Subscription
    Condition: SubEnabled
    Properties:
      Endpoint: !GetAtt Queue.Arn
"#);
        let path = vec!["Resources".into(), "Sub".into(), "Properties".into(), "Endpoint".into()];
        let scenarios = is_resource_available(&tmpl, &ast, &path, "Queue");
        assert!(scenarios.is_empty(), "Expected no issues but got: {:?}", scenarios);
    }
}
