// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

//! Fn::Equals evaluation with parameter awareness.
//! Mirrors Python's `cfnlint.conditions._equals`.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

use crate::ast::AstNode;

use super::sat::Expr;

/// Compute a SHA1 hash of an AstNode for consistent identity.
/// Mirrors Python's `get_hash()`.
pub fn get_hash(node: &AstNode) -> String {
    let s = ast_to_canonical(node);
    let mut hasher = DefaultHasher::new();
    s.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

/// Canonical string representation for hashing.
/// Mirrors Python's json.dumps(o, sort_keys=True).
fn ast_to_canonical(node: &AstNode) -> String {
    match node {
        AstNode::String(s) => format!("\"{}\"", s.value),
        AstNode::Number(n) => n.value.to_string(),
        AstNode::Bool(b) => b.value.to_string(),
        AstNode::Null(_) => "null".to_string(),
        AstNode::Array(arr) => {
            let items: Vec<String> = arr.elements.iter().map(ast_to_canonical).collect();
            format!("[{}]", items.join(", "))
        }
        AstNode::Object(obj) => {
            let mut pairs: Vec<(String, String)> = obj
                .iter()
                .map(|(k, v)| (k.to_string(), ast_to_canonical(v)))
                .collect();
            pairs.sort_by(|a, b| a.0.cmp(&b.0));
            let items: Vec<String> = pairs
                .iter()
                .map(|(k, v)| format!("\"{}\": {}", k, v))
                .collect();
            format!("{{{}}}", items.join(", "))
        }
        AstNode::Function(func) => {
            // Functions like Ref are stored as {"Ref": args}
            let args = ast_to_canonical(&func.args);
            format!("{{\"{}\": {}}}", func.name, args)
        }
    }
}

/// One side of an Fn::Equals — either a literal string or a function (e.g. Ref).
/// Mirrors Python's `EqualParameter`.
#[derive(Debug, Clone)]
pub struct EqualParameter {
    pub hash: String,
    pub satisfiable: bool,
}

impl EqualParameter {
    pub fn from_ast(node: &AstNode) -> Self {
        let hash = get_hash(node);
        let satisfiable = matches!(node, AstNode::Function(f) if f.name == "Ref");
        Self { hash, satisfiable }
    }
}

/// An Fn::Equals expression.
/// Mirrors Python's `Equal`.
#[derive(Debug, Clone)]
pub struct Equal {
    pub hash: String,
    pub is_static: Option<bool>,
    left: EqualSide,
    right: EqualSide,
}

#[derive(Debug, Clone)]
enum EqualSide {
    Literal(String, String), // (value, hash)
    Parameter(EqualParameter),
}

impl Equal {
    /// Parse from two AstNode values (the Fn::Equals array elements).
    pub fn new(left: &AstNode, right: &AstNode) -> Result<Self, String> {
        // Sort for consistency
        let left_canonical = ast_to_canonical(left);
        let right_canonical = ast_to_canonical(right);
        let (sorted_l, sorted_r) = if left_canonical <= right_canonical {
            (left, right)
        } else {
            (right, left)
        };

        let left_side = init_side(sorted_l);
        let right_side = init_side(sorted_r);

        // Hash the sorted pair
        let hash = {
            let s = format!(
                "[{}, {}]",
                ast_to_canonical(sorted_l),
                ast_to_canonical(sorted_r)
            );
            let mut hasher = DefaultHasher::new();
            s.hash(&mut hasher);
            format!("{:016x}", hasher.finish())
        };

        let is_static = match (&left_side, &right_side) {
            (EqualSide::Literal(_, h1), EqualSide::Literal(_, h2)) => Some(h1 == h2),
            (EqualSide::Parameter(p1), EqualSide::Parameter(p2)) => {
                if p1.hash == p2.hash {
                    Some(true)
                } else {
                    None
                }
            }
            _ => None,
        };

        Ok(Self {
            hash,
            is_static,
            left: left_side,
            right: right_side,
        })
    }

    pub fn parameters(&self) -> Vec<&EqualParameter> {
        let mut params = Vec::new();
        if let EqualSide::Parameter(p) = &self.left {
            params.push(p);
        }
        if let EqualSide::Parameter(p) = &self.right {
            params.push(p);
        }
        params
    }

    pub fn has_parameter_hash(&self, hash: &str) -> bool {
        self.parameters().iter().any(|p| p.hash == hash)
    }

    /// Get the hash of the static (literal) side, if any.
    pub fn static_value_hash(&self) -> Option<String> {
        match (&self.left, &self.right) {
            (EqualSide::Literal(_, h), EqualSide::Parameter(_))
            | (EqualSide::Parameter(_), EqualSide::Literal(_, h)) => Some(h.clone()),
            _ => None,
        }
    }

    pub fn test_with_hash(&self, param_hash: &str, value: &str) -> bool {
        if let Some(is_static) = self.is_static {
            return is_static;
        }
        match (&self.left, &self.right) {
            (EqualSide::Parameter(p), EqualSide::Literal(v, _)) if p.hash == param_hash => {
                value == v
            }
            (EqualSide::Literal(v, _), EqualSide::Parameter(p)) if p.hash == param_hash => {
                value == v
            }
            _ => false,
        }
    }

    pub fn build_expr(
        &self,
        solver_params: &std::collections::HashMap<String, usize>,
        static_equals: &std::collections::HashMap<String, bool>,
    ) -> Expr {
        if let Some(&var) = solver_params.get(&self.hash) {
            Expr::Var(var)
        } else if let Some(&val) = static_equals.get(&self.hash) {
            Expr::Const(val)
        } else {
            Expr::Const(true)
        }
    }
}

fn init_side(node: &AstNode) -> EqualSide {
    match node {
        AstNode::String(s) => EqualSide::Literal(s.value.clone(), get_hash(node)),
        AstNode::Function(_) | AstNode::Object(_) => {
            EqualSide::Parameter(EqualParameter::from_ast(node))
        }
        AstNode::Number(n) => {
            let s = n.value.to_string();
            EqualSide::Literal(s, get_hash(node))
        }
        AstNode::Bool(b) => {
            let s = b.value.to_string();
            EqualSide::Literal(s, get_hash(node))
        }
        _ => EqualSide::Literal(String::new(), get_hash(node)),
    }
}

/// Helper to build a Ref function node for hashing.
fn make_ref_node(name: &str) -> AstNode {
    AstNode::Function(crate::ast::FunctionNode {
        name: "Ref".to_string(),
        args: Box::new(AstNode::String(crate::ast::StringNode {
            value: name.to_string(),
            span: crate::ast::Span::default(),
        })),
        span: crate::ast::Span::default(),
    })
}

/// Get hash for a Ref to a parameter name.
pub fn ref_hash(param_name: &str) -> String {
    get_hash(&make_ref_node(param_name))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;

    fn str_node(s: &str) -> AstNode {
        AstNode::String(StringNode {
            value: s.into(),
            span: Span::default(),
        })
    }

    fn ref_node(name: &str) -> AstNode {
        AstNode::Function(FunctionNode {
            name: "Ref".into(),
            args: Box::new(str_node(name)),
            span: Span::default(),
        })
    }

    #[test]
    fn test_static_equals_true() {
        let eq = Equal::new(&str_node("a"), &str_node("a")).unwrap();
        assert_eq!(eq.is_static, Some(true));
    }

    #[test]
    fn test_static_equals_false() {
        let eq = Equal::new(&str_node("a"), &str_node("b")).unwrap();
        assert_eq!(eq.is_static, Some(false));
    }

    #[test]
    fn test_dynamic_equals() {
        let eq = Equal::new(&ref_node("Env"), &str_node("prod")).unwrap();
        assert_eq!(eq.is_static, None);
        assert_eq!(eq.parameters().len(), 1);
    }

    #[test]
    fn test_hash_consistency() {
        let eq1 = Equal::new(&ref_node("Env"), &str_node("prod")).unwrap();
        let eq2 = Equal::new(&str_node("prod"), &ref_node("Env")).unwrap();
        assert_eq!(eq1.hash, eq2.hash);
    }
}
