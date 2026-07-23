// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

//! Condition tree nodes (And, Or, Not, Equals, Named).
//! Mirrors Python's `cfnlint.conditions._condition`.

use std::collections::HashMap;

use crate::ast::AstNode;

use super::equals::Equal;
use super::sat::Expr;

/// Maximum structural nesting depth for a condition expression tree. Guards
/// against stack overflow from adversarially deep Fn::And/Or/Not nesting that
/// the named-cycle `visited` set cannot detect.
const MAX_CONDITION_DEPTH: usize = 50;

/// A condition tree node.
#[derive(Debug, Clone)]
pub enum ConditionNode {
    Equals(Equal),
    And(Vec<ConditionNode>),
    Or(Vec<ConditionNode>),
    Not(Box<ConditionNode>),
    Named(String, Box<ConditionNode>),
}

impl ConditionNode {
    /// Parse a condition expression from an AstNode.
    /// Handles both Object form ({"Fn::Equals": [...]}) and Function form
    /// (parsed by cfn-ast as AstNode::Function).
    pub fn parse(
        node: &AstNode,
        all_conditions: &HashMap<String, AstNode>,
    ) -> Result<Self, String> {
        let mut visited = std::collections::HashSet::new();
        Self::parse_inner(node, all_conditions, &mut visited, 0)
    }

    fn parse_inner(
        node: &AstNode,
        all_conditions: &HashMap<String, AstNode>,
        visited: &mut std::collections::HashSet<String>,
        depth: usize,
    ) -> Result<Self, String> {
        // The `visited` set only catches *named* condition cycles. Structural
        // nesting (deeply nested Fn::And/Or/Not with no named conditions) would
        // still overflow the stack, so cap the structural depth as well.
        if depth > MAX_CONDITION_DEPTH {
            return Err(format!(
                "Condition nesting exceeded maximum depth ({MAX_CONDITION_DEPTH})"
            ));
        }

        // Function node form (cfn-ast parses Fn::Equals, Condition, etc. as Function)
        if let AstNode::Function(func) = node {
            return match func.name.as_str() {
                "Fn::Equals" => {
                    let arr = func
                        .args
                        .as_array()
                        .ok_or("Fn::Equals value should be an array")?;
                    if arr.elements.len() != 2 {
                        return Err("Fn::Equals must have exactly 2 elements".into());
                    }
                    Ok(ConditionNode::Equals(Equal::new(
                        &arr.elements[0],
                        &arr.elements[1],
                    )?))
                }
                "Fn::And" => {
                    let arr = func
                        .args
                        .as_array()
                        .ok_or("Fn::And value should be an array")?;
                    let children: Result<Vec<_>, _> = arr
                        .elements
                        .iter()
                        .map(|v| ConditionNode::parse_inner(v, all_conditions, visited, depth + 1))
                        .collect();
                    Ok(ConditionNode::And(children?))
                }
                "Fn::Or" => {
                    let arr = func
                        .args
                        .as_array()
                        .ok_or("Fn::Or value should be an array")?;
                    let children: Result<Vec<_>, _> = arr
                        .elements
                        .iter()
                        .map(|v| ConditionNode::parse_inner(v, all_conditions, visited, depth + 1))
                        .collect();
                    Ok(ConditionNode::Or(children?))
                }
                "Fn::Not" => {
                    let arr = func
                        .args
                        .as_array()
                        .ok_or("Fn::Not value should be an array")?;
                    if arr.elements.len() != 1 {
                        return Err("Condition length must be 1".into());
                    }
                    Ok(ConditionNode::Not(Box::new(ConditionNode::parse_inner(
                        &arr.elements[0],
                        all_conditions,
                        visited,
                        depth + 1,
                    )?)))
                }
                "Condition" => {
                    let name = func
                        .args
                        .as_str()
                        .ok_or("Condition value must be a string")?;
                    if !visited.insert(name.to_string()) {
                        return Err(format!("Circular condition reference: {name}"));
                    }
                    let sub = all_conditions
                        .get(name)
                        .ok_or(format!("Condition {name} not found"))?;
                    let result = ConditionNode::Named(
                        name.to_string(),
                        Box::new(ConditionNode::parse_inner(
                            sub,
                            all_conditions,
                            visited,
                            depth + 1,
                        )?),
                    );
                    visited.remove(name);
                    Ok(result)
                }
                _ => Err(format!("Unknown function ({}) in condition", func.name)),
            };
        }

        // Object form ({"Fn::Equals": [...]} as a plain object)
        let obj = node
            .as_object()
            .ok_or("Condition value must be an object or function")?;
        if obj.len() != 1 {
            return Err("Condition value must be an object of length 1".into());
        }

        let (key, val) = obj.iter().next().unwrap();
        match key {
            "Fn::Equals" => {
                let arr = val
                    .as_array()
                    .ok_or("Fn::Equals value should be an array")?;
                if arr.elements.len() != 2 {
                    return Err("Fn::Equals must have exactly 2 elements".into());
                }
                Ok(ConditionNode::Equals(Equal::new(
                    &arr.elements[0],
                    &arr.elements[1],
                )?))
            }
            "Fn::And" => {
                let arr = val.as_array().ok_or("Fn::And value should be an array")?;
                let children: Result<Vec<_>, _> = arr
                    .elements
                    .iter()
                    .map(|v| ConditionNode::parse_inner(v, all_conditions, visited, depth + 1))
                    .collect();
                Ok(ConditionNode::And(children?))
            }
            "Fn::Or" => {
                let arr = val.as_array().ok_or("Fn::Or value should be an array")?;
                let children: Result<Vec<_>, _> = arr
                    .elements
                    .iter()
                    .map(|v| ConditionNode::parse_inner(v, all_conditions, visited, depth + 1))
                    .collect();
                Ok(ConditionNode::Or(children?))
            }
            "Fn::Not" => {
                let arr = val.as_array().ok_or("Fn::Not value should be an array")?;
                if arr.elements.len() != 1 {
                    return Err("Condition length must be 1".into());
                }
                Ok(ConditionNode::Not(Box::new(ConditionNode::parse_inner(
                    &arr.elements[0],
                    all_conditions,
                    visited,
                    depth + 1,
                )?)))
            }
            "Condition" => {
                let name = val.as_str().ok_or("Condition value must be a string")?;
                if !visited.insert(name.to_string()) {
                    return Err(format!("Circular condition reference: {name}"));
                }
                let sub = all_conditions
                    .get(name)
                    .ok_or(format!("Condition {name} not found"))?;
                let result = ConditionNode::Named(
                    name.to_string(),
                    Box::new(ConditionNode::parse_inner(
                        sub,
                        all_conditions,
                        visited,
                        depth + 1,
                    )?),
                );
                visited.remove(name);
                Ok(result)
            }
            _ => Err(format!("Unknown key ({key}) in condition")),
        }
    }

    pub fn equals(&self) -> Vec<&Equal> {
        match self {
            ConditionNode::Equals(eq) => vec![eq],
            ConditionNode::And(children) | ConditionNode::Or(children) => {
                children.iter().flat_map(|c| c.equals()).collect()
            }
            ConditionNode::Not(child) | ConditionNode::Named(_, child) => child.equals(),
        }
    }

    pub fn build_expr(
        &self,
        solver_params: &HashMap<String, usize>,
        static_equals: &HashMap<String, bool>,
    ) -> Expr {
        match self {
            ConditionNode::Equals(eq) => eq.build_expr(solver_params, static_equals),
            ConditionNode::And(children) => Expr::And(
                children
                    .iter()
                    .map(|c| c.build_expr(solver_params, static_equals))
                    .collect(),
            ),
            ConditionNode::Or(children) => Expr::Or(
                children
                    .iter()
                    .map(|c| c.build_expr(solver_params, static_equals))
                    .collect(),
            ),
            ConditionNode::Not(child) => {
                Expr::Not(Box::new(child.build_expr(solver_params, static_equals)))
            }
            ConditionNode::Named(_, child) => child.build_expr(solver_params, static_equals),
        }
    }
}

/// A named condition from the template's Conditions section.
#[derive(Debug, Clone)]
pub struct ConditionNamed {
    pub name: String,
    root: ConditionNode,
}

impl ConditionNamed {
    pub fn new(name: &str, all_conditions: &HashMap<String, AstNode>) -> Result<Self, String> {
        let value = all_conditions
            .get(name)
            .ok_or(format!("Condition {name} not found"))?;
        Ok(Self {
            name: name.to_string(),
            root: ConditionNode::parse(value, all_conditions)?,
        })
    }

    pub fn equals(&self) -> Vec<&Equal> {
        self.root.equals()
    }

    pub fn build_expr(
        &self,
        solver_params: &HashMap<String, usize>,
        static_equals: &HashMap<String, bool>,
    ) -> Expr {
        self.root.build_expr(solver_params, static_equals)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use crate::ast::{ArrayNode, FunctionNode, Span, StringNode};
    use crate::parser;

    fn parse_conditions(yaml: &[u8]) -> HashMap<String, AstNode> {
        let ast = parser::parse(yaml).unwrap();
        let obj = ast.as_object().unwrap();
        obj.iter()
            .map(|(k, v)| (k.to_string(), v.clone()))
            .collect()
    }

    #[test]
    fn test_parse_equals() {
        let conds = parse_conditions(
            br#"
IsProd:
  Fn::Equals:
    - !Ref Env
    - prod
"#,
        );
        let c = ConditionNamed::new("IsProd", &conds).unwrap();
        assert_eq!(c.equals().len(), 1);
    }

    #[test]
    fn test_parse_and() {
        let conds = parse_conditions(
            br#"
IsProd:
  Fn::Equals:
    - !Ref Env
    - prod
IsUsEast1:
  Fn::Equals:
    - !Ref "AWS::Region"
    - us-east-1
Both:
  Fn::And:
    - Condition: IsProd
    - Condition: IsUsEast1
"#,
        );
        let c = ConditionNamed::new("Both", &conds).unwrap();
        assert_eq!(c.equals().len(), 2);
    }

    #[test]
    fn test_parse_not() {
        let conds = parse_conditions(
            br#"
IsProd:
  Fn::Equals:
    - !Ref Env
    - prod
IsNotProd:
  Fn::Not:
    - Condition: IsProd
"#,
        );
        let c = ConditionNamed::new("IsNotProd", &conds).unwrap();
        assert_eq!(c.equals().len(), 1);
    }

    #[test]
    fn test_parse_or() {
        let conds = parse_conditions(
            br#"
IsProd:
  Fn::Equals:
    - !Ref Env
    - prod
IsDev:
  Fn::Equals:
    - !Ref Env
    - dev
Either:
  Fn::Or:
    - Condition: IsProd
    - Condition: IsDev
"#,
        );
        let c = ConditionNamed::new("Either", &conds).unwrap();
        assert_eq!(c.equals().len(), 2);
    }

    // ── C42: structural depth limit for adversarially nested conditions ──

    fn run_with_timeout<F: FnOnce() + Send + 'static>(secs: u64, f: F) {
        use std::sync::mpsc::{channel, RecvTimeoutError};
        use std::time::Duration;
        let (tx, rx) = channel();
        let handle = std::thread::spawn(move || {
            f();
            let _ = tx.send(());
        });
        match rx.recv_timeout(Duration::from_secs(secs)) {
            Ok(()) => handle.join().unwrap(),
            Err(RecvTimeoutError::Timeout) => {
                panic!("did not finish within {secs}s — condition depth guard likely regressed")
            }
            Err(RecvTimeoutError::Disconnected) => handle.join().unwrap(),
        }
    }

    fn func(name: &str, args: AstNode) -> AstNode {
        AstNode::Function(FunctionNode {
            name: name.to_string(),
            args: Box::new(args),
            span: Span::default(),
        })
    }

    fn str_node(s: &str) -> AstNode {
        AstNode::String(StringNode {
            value: s.to_string(),
            span: Span::default(),
        })
    }

    #[test]
    fn test_deeply_nested_and_errors_not_overflow() {
        run_with_timeout(10, || {
            // Start from a valid Fn::Equals, then wrap it in 100 layers of Fn::And.
            // The `visited` set only catches named cycles, so without a structural
            // depth cap this overflows the stack.
            let mut node = func(
                "Fn::Equals",
                AstNode::Array(ArrayNode {
                    elements: vec![str_node("a"), str_node("a")],
                    span: Span::default(),
                }),
            );
            for _ in 0..100 {
                node = func(
                    "Fn::And",
                    AstNode::Array(ArrayNode {
                        elements: vec![node],
                        span: Span::default(),
                    }),
                );
            }
            let conds: HashMap<String, AstNode> = HashMap::new();
            let err = ConditionNode::parse(&node, &conds).unwrap_err();
            assert!(
                err.contains("maximum depth"),
                "expected a depth-limit error, got: {err}"
            );
        });
    }

    #[test]
    fn test_deeply_nested_not_errors_not_overflow() {
        run_with_timeout(10, || {
            let mut node = func(
                "Fn::Equals",
                AstNode::Array(ArrayNode {
                    elements: vec![str_node("a"), str_node("a")],
                    span: Span::default(),
                }),
            );
            for _ in 0..100 {
                node = func(
                    "Fn::Not",
                    AstNode::Array(ArrayNode {
                        elements: vec![node],
                        span: Span::default(),
                    }),
                );
            }
            let conds: HashMap<String, AstNode> = HashMap::new();
            let err = ConditionNode::parse(&node, &conds).unwrap_err();
            assert!(err.contains("maximum depth"), "got: {err}");
        });
    }

    #[test]
    fn test_shallow_nesting_still_parses() {
        // A modestly nested condition (below the cap) must still parse fine.
        let mut node = func(
            "Fn::Equals",
            AstNode::Array(ArrayNode {
                elements: vec![str_node("a"), str_node("a")],
                span: Span::default(),
            }),
        );
        for _ in 0..5 {
            node = func(
                "Fn::And",
                AstNode::Array(ArrayNode {
                    elements: vec![node],
                    span: Span::default(),
                }),
            );
        }
        let conds: HashMap<String, AstNode> = HashMap::new();
        assert!(ConditionNode::parse(&node, &conds).is_ok());
    }
}
