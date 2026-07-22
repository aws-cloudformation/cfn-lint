use std::collections::{BTreeMap, HashMap, HashSet};

use crate::ast::{self, AstNode};
use crate::conditions::Conditions;
use crate::graph::get_conditions_from_path;
use crate::helpers::SUB_VARIABLE_REGEX;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// The set of condition assignments that must hold for a dependency edge to
/// exist (a conjunction). An empty gate means the edge is unconditional.
type Gate = BTreeMap<String, bool>;

/// Dependency graph: resource name -> (dependency name -> gate).
type DepGraph = HashMap<String, HashMap<String, Gate>>;

pub struct E3004;

impl CfnLintRule for E3004 {
    fn id(&self) -> &str {
        "E3004"
    }
    fn short_description(&self) -> &str {
        "Resource dependencies are not circular"
    }
    fn description(&self) -> &str {
        "Check for circular dependencies between resources"
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
        let resource_names: HashSet<&str> = template.resources.keys().map(|s| s.as_str()).collect();
        let resources_node = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(o) => o,
            None => return vec![],
        };

        // Build condition-aware dependency graph: resource -> (dep -> gate).
        let conditions = Conditions::from_template(template);
        let mut graph: DepGraph = HashMap::new();
        for name in template.resources.keys() {
            graph.entry(name.clone()).or_default();
        }
        for (name, resource) in &template.resources {
            // Explicit DependsOn edges are unconditional.
            for dep in &resource.depends_on {
                if resource_names.contains(dep.as_str()) {
                    add_edge(&mut graph, name, dep, Gate::new());
                }
            }
            // Implicit deps from Ref, GetAtt, Sub within this resource's body.
            if let Some(res_node) = resources_node.get(name.as_str()) {
                collect_resource_refs(name, res_node, root, &resource_names, &mut graph);
            }
        }

        // Find cycles - report one error per resource in a (satisfiable) cycle.
        let mut issues = Vec::new();
        let mut reported: HashSet<String> = HashSet::new();
        let empty_gate = Gate::new();

        for name in template.resources.keys() {
            let mut visited = HashSet::new();
            let mut stack = Vec::new();
            let mut edge_gates: Vec<&Gate> = vec![&empty_gate];
            let cycle = find_cycle(
                name.as_str(),
                &graph,
                &conditions,
                &mut visited,
                &mut stack,
                &mut edge_gates,
            );
            if let Some(cycle) = cycle {
                for res in &cycle {
                    if reported.contains(res) {
                        continue;
                    }
                    reported.insert(res.clone());
                    // Find what it cycles with
                    let deps: Vec<&str> = graph
                        .get(res.as_str())
                        .map(|d| {
                            d.keys()
                                .filter(|dep| cycle.contains(dep))
                                .map(|s| s.as_str())
                                .collect()
                        })
                        .unwrap_or_default();
                    let pos = resources_node
                        .get(res.as_str())
                        .map(|n| n.span())
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

/// Add (or merge) a dependency edge `source -> target` guarded by `gate`.
///
/// When the same edge is discovered under several gates it exists under their
/// *disjunction*. We keep only the constraints common to every occurrence
/// (intersection). This under-constrains rather than over-constrains, so a real
/// cycle can never be suppressed by mistake.
fn add_edge(graph: &mut DepGraph, source: &str, target: &str, gate: Gate) {
    let targets = graph.entry(source.to_string()).or_default();
    match targets.get_mut(target) {
        Some(existing) => existing.retain(|k, v| gate.get(k) == Some(v)),
        None => {
            targets.insert(target.to_string(), gate);
        }
    }
}

/// The condition gate for a reference located at `path`: the single-valued
/// condition assignments that must hold for control flow to reach it (resource
/// `Condition` plus any `Fn::If` branches on the path).
fn path_gate(root: &AstNode, path: &[String]) -> Gate {
    let mut gate = Gate::new();
    for (cond, values) in get_conditions_from_path(root, path) {
        // A condition forced to both true and false along the path doesn't
        // actually constrain the edge, so it is not part of the gate.
        if values.len() == 1 {
            gate.insert(cond, *values.iter().next().unwrap());
        }
    }
    gate
}

fn collect_resource_refs(
    resource_name: &str,
    res_node: &AstNode,
    root: &AstNode,
    resources: &HashSet<&str>,
    graph: &mut DepGraph,
) {
    let base = vec!["Resources".to_string(), resource_name.to_string()];
    ast::walk(res_node, &base, &mut |n, path| {
        if let AstNode::Function(func) = n {
            match func.name.as_str() {
                "Ref" => {
                    if let Some(name) = func.args.as_str() {
                        if resources.contains(name) {
                            add_edge(graph, resource_name, name, path_gate(root, path));
                        }
                    }
                }
                "Fn::GetAtt" => {
                    let res_name = if let Some(s) = func.args.as_str() {
                        s.split('.').next().map(|s| s.to_string())
                    } else if let Some(arr) = func.args.as_array() {
                        arr.elements
                            .first()
                            .and_then(|e| e.as_str())
                            .map(|s| s.to_string())
                    } else {
                        None
                    };
                    if let Some(name) = res_name {
                        if resources.contains(name.as_str()) {
                            add_edge(graph, resource_name, &name, path_gate(root, path));
                        }
                    }
                }
                "Fn::Sub" => {
                    // Split the two Sub forms: a bare string, or `[template, map]`.
                    // Variable names defined in the substitution map shadow resource
                    // names and must NOT create dependency edges.
                    let (template_str, sub_keys): (Option<String>, HashSet<&str>) =
                        if let Some(s) = func.args.as_str() {
                            (Some(s.to_string()), HashSet::new())
                        } else if let Some(arr) = func.args.as_array() {
                            let tmpl = arr
                                .elements
                                .first()
                                .and_then(|e| e.as_str())
                                .map(|s| s.to_string());
                            let keys: HashSet<&str> = if arr.elements.len() == 2 {
                                arr.elements[1]
                                    .as_object()
                                    .map(|o| o.keys().collect())
                                    .unwrap_or_default()
                            } else {
                                HashSet::new()
                            };
                            (tmpl, keys)
                        } else {
                            (None, HashSet::new())
                        };
                    if let Some(s) = template_str {
                        let gate = path_gate(root, path);
                        for cap in SUB_VARIABLE_REGEX.captures_iter(&s) {
                            let var = cap[1].trim();
                            let name = var.split('.').next().unwrap_or(var);
                            if sub_keys.contains(name) {
                                continue;
                            }
                            if resources.contains(name) {
                                add_edge(graph, resource_name, name, gate.clone());
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

/// Combine the gates of every edge on a cycle into a single conjunction.
///
/// Returns `None` if the conjunction is contradictory (some condition is
/// required to be both true and false), which means the cycle can never form.
fn combine_gates(gates: &[&Gate], closing: &Gate) -> Option<HashMap<String, bool>> {
    let mut combined: HashMap<String, bool> = HashMap::new();
    for gate in gates.iter().copied().chain(std::iter::once(closing)) {
        for (cond, value) in gate {
            match combined.get(cond) {
                Some(existing) if existing != value => return None,
                _ => {
                    combined.insert(cond.clone(), *value);
                }
            }
        }
    }
    Some(combined)
}

/// Depth-first search for a *reachable* dependency cycle.
///
/// `edge_gates[i]` is the gate of the edge into `stack[i]` (index 0 is a
/// sentinel for the DFS root). When a back-edge closes a cycle, the gates of all
/// edges on the cycle are conjoined; the cycle is only reported if that
/// conjunction is satisfiable under the template's conditions. Condition-gated
/// pseudo-cycles (e.g. mutually-exclusive `Fn::If` branches) are suppressed, and
/// the search continues so a genuine cycle behind them is still found.
fn find_cycle<'a>(
    start: &'a str,
    graph: &'a DepGraph,
    conditions: &Conditions,
    visited: &mut HashSet<&'a str>,
    stack: &mut Vec<&'a str>,
    edge_gates: &mut Vec<&'a Gate>,
) -> Option<Vec<String>> {
    visited.insert(start);
    stack.push(start);

    if let Some(deps) = graph.get(start) {
        for (dep, gate) in deps {
            let dep_ref = dep.as_str();
            if !graph.contains_key(dep_ref) {
                continue;
            }
            if !visited.contains(dep_ref) {
                edge_gates.push(gate);
                if let Some(cycle) =
                    find_cycle(dep_ref, graph, conditions, visited, stack, edge_gates)
                {
                    return Some(cycle);
                }
                edge_gates.pop();
            } else if let Some(idx) = stack.iter().position(|&n| n == dep_ref) {
                // Cycle closes on stack[idx]. Its edges are edge_gates[idx+1..]
                // (edges between the cycle's stack nodes) plus the closing edge.
                if let Some(combined) = combine_gates(&edge_gates[idx + 1..], gate) {
                    if combined.is_empty() || conditions.is_condition_set_satisfiable(&combined) {
                        return Some(stack[idx..].iter().map(|s| s.to_string()).collect());
                    }
                }
                // Otherwise the cycle is condition-gated and unsatisfiable — not a
                // real cycle. Suppress it and keep searching other dependencies.
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

    #[test]
    fn test_sub_literal_escape_no_cycle() {
        // C51/C56: `${!B}` is a literal escape, not a reference to resource B,
        // so it must not create an A -> B dependency edge (hence no cycle).
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Sub "literal-${!B}"
  B:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Ref A
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert!(
            issues.is_empty(),
            "escaped ${{!B}} must not create a dependency: {:?}",
            issues
        );
    }

    #[test]
    fn test_sub_still_creates_real_dependency() {
        // Control: an unescaped `${B}` in A plus `!Ref A` in B is a real cycle.
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Sub "name-${B}"
  B:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Ref A
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert_eq!(
            issues.len(),
            2,
            "unescaped ${{B}} should cycle: {:?}",
            issues
        );
    }

    #[test]
    fn test_sub_map_key_shadows_resource_no_cycle() {
        // C51: `${B}` resolves to the Fn::Sub substitution map key, not resource
        // B, so it must not create an A -> B edge (hence no false cycle).
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName:
        Fn::Sub:
          - "name-${B}"
          - B: literal-value
  B:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !Ref A
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert!(
            issues.is_empty(),
            "sub-map key shadowing resource B must not cycle: {:?}",
            issues
        );
    }

    #[test]
    fn test_conditional_pseudo_cycle_suppressed() {
        // C52: A -> B only when Cond is true; B -> A only when Cond is false.
        // The two edges are mutually exclusive, so no runtime cycle exists.
        let yaml = br#"
Parameters:
  Env:
    Type: String
Conditions:
  Cond:
    Fn::Equals: [!Ref Env, prod]
Resources:
  A:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !If [Cond, !Ref B, "x"]
  B:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !If [Cond, "y", !Ref A]
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert!(
            issues.is_empty(),
            "mutually-exclusive conditional edges must not cycle: {:?}",
            issues
        );
    }

    #[test]
    fn test_conditional_same_branch_real_cycle() {
        // C52 control: both edges are gated by the SAME condition value, so when
        // Cond is true a genuine cycle exists and must still be reported.
        let yaml = br#"
Parameters:
  Env:
    Type: String
Conditions:
  Cond:
    Fn::Equals: [!Ref Env, prod]
Resources:
  A:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !If [Cond, !Ref B, "x"]
  B:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: !If [Cond, !Ref A, "y"]
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3004.validate_template(&tmpl, &ast);
        assert_eq!(
            issues.len(),
            2,
            "same-condition cycle should be reported: {:?}",
            issues
        );
    }
}

crate::register_cfn_lint_rule!(E3004);
