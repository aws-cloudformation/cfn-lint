// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

//! Minimal CNF-based SAT solver.
//! Replaces Python's SymPy satisfiable() / EncodedCNF.

use std::collections::HashMap;

/// A boolean expression tree (before CNF conversion).
#[derive(Debug, Clone)]
pub enum Expr {
    Const(bool),
    Var(usize),
    Not(Box<Expr>),
    And(Vec<Expr>),
    Or(Vec<Expr>),
}

/// A CNF formula: conjunction of clauses.
/// Each clause is a disjunction of literals (var_index, positive).
#[derive(Debug, Clone)]
pub struct CnfFormula {
    clauses: Vec<Vec<(usize, bool)>>,
    var_names: HashMap<String, usize>,
    num_vars: usize,
}

impl CnfFormula {
    pub fn new() -> Self {
        Self {
            clauses: Vec::new(),
            var_names: HashMap::new(),
            num_vars: 0,
        }
    }

    /// Get or create a variable index for a named variable.
    pub fn get_or_create_var(&mut self, name: &str) -> usize {
        if let Some(&idx) = self.var_names.get(name) {
            idx
        } else {
            let idx = self.num_vars;
            self.num_vars += 1;
            self.var_names.insert(name.to_string(), idx);
            idx
        }
    }

    /// Add a raw clause (disjunction of literals).
    pub fn add_clause(&mut self, clause: Vec<(usize, bool)>) {
        if !clause.is_empty() {
            self.clauses.push(clause);
        }
    }

    /// Convert an expression to CNF clauses and add them.
    pub fn add_expr(&mut self, expr: &Expr) {
        let clauses = expr_to_cnf(expr, &mut self.num_vars);
        self.clauses.extend(clauses);
    }

    /// Check if the formula is satisfiable using DPLL.
    pub fn is_satisfiable(&self) -> bool {
        if self.clauses.is_empty() {
            return true;
        }
        dpll(&self.clauses, self.num_vars)
    }
}

/// Convert an expression to CNF clauses using Tseitin transformation.
fn expr_to_cnf(expr: &Expr, num_vars: &mut usize) -> Vec<Vec<(usize, bool)>> {
    let mut clauses = Vec::new();
    let root = tseitin(expr, &mut clauses, num_vars);
    // Assert the root literal is true
    clauses.push(vec![(root, true)]);
    clauses
}

/// Tseitin transformation: returns a variable index representing this expression.
fn tseitin(
    expr: &Expr,
    clauses: &mut Vec<Vec<(usize, bool)>>,
    num_vars: &mut usize,
) -> usize {
    match expr {
        Expr::Const(true) => {
            let v = fresh(num_vars);
            clauses.push(vec![(v, true)]);
            v
        }
        Expr::Const(false) => {
            let v = fresh(num_vars);
            clauses.push(vec![(v, false)]);
            v
        }
        Expr::Var(idx) => *idx,
        Expr::Not(inner) => {
            let inner_v = tseitin(inner, clauses, num_vars);
            let v = fresh(num_vars);
            // v <=> ~inner_v
            // v => ~inner_v: ~v | ~inner_v
            clauses.push(vec![(v, false), (inner_v, false)]);
            // ~inner_v => v: inner_v | v
            clauses.push(vec![(inner_v, true), (v, true)]);
            v
        }
        Expr::And(children) => {
            if children.is_empty() {
                let v = fresh(num_vars);
                clauses.push(vec![(v, true)]);
                return v;
            }
            if children.len() == 1 {
                return tseitin(&children[0], clauses, num_vars);
            }
            let child_vars: Vec<usize> = children
                .iter()
                .map(|c| tseitin(c, clauses, num_vars))
                .collect();
            let v = fresh(num_vars);
            // v => (c1 & c2 & ...): for each ci, ~v | ci
            for &cv in &child_vars {
                clauses.push(vec![(v, false), (cv, true)]);
            }
            // (c1 & c2 & ...) => v: ~c1 | ~c2 | ... | v
            let mut clause: Vec<(usize, bool)> = child_vars.iter().map(|&cv| (cv, false)).collect();
            clause.push((v, true));
            clauses.push(clause);
            v
        }
        Expr::Or(children) => {
            if children.is_empty() {
                let v = fresh(num_vars);
                clauses.push(vec![(v, false)]);
                return v;
            }
            if children.len() == 1 {
                return tseitin(&children[0], clauses, num_vars);
            }
            let child_vars: Vec<usize> = children
                .iter()
                .map(|c| tseitin(c, clauses, num_vars))
                .collect();
            let v = fresh(num_vars);
            // v => (c1 | c2 | ...): ~v | c1 | c2 | ...
            let mut clause: Vec<(usize, bool)> = child_vars.iter().map(|&cv| (cv, true)).collect();
            clause.push((v, false));
            clauses.push(clause);
            // (c1 | c2 | ...) => v: for each ci, ~ci | v
            for &cv in &child_vars {
                clauses.push(vec![(cv, false), (v, true)]);
            }
            v
        }
    }
}

fn fresh(num_vars: &mut usize) -> usize {
    let v = *num_vars;
    *num_vars += 1;
    v
}

/// DPLL SAT solver.
fn dpll(clauses: &[Vec<(usize, bool)>], num_vars: usize) -> bool {
    let mut assignment: Vec<Option<bool>> = vec![None; num_vars];
    dpll_inner(clauses, &mut assignment)
}

fn dpll_inner(clauses: &[Vec<(usize, bool)>], assignment: &mut Vec<Option<bool>>) -> bool {
    // Unit propagation
    loop {
        let mut changed = false;

        // Check for empty clause (unsatisfiable) or all satisfied
        let mut all_satisfied = true;
        for clause in clauses {
            let mut satisfied = false;
            let mut unset_count = 0;
            let mut last_unset: Option<(usize, bool)> = None;

            for &(var, positive) in clause {
                if let Some(val) = assignment[var] {
                    if val == positive {
                        satisfied = true;
                        break;
                    }
                } else {
                    unset_count += 1;
                    last_unset = Some((var, positive));
                }
            }

            if satisfied {
                continue;
            }

            all_satisfied = false;

            if unset_count == 0 {
                return false; // Empty clause — unsatisfiable
            }

            if unset_count == 1 {
                // Unit clause — must set this literal
                let (var, positive) = last_unset.unwrap();
                assignment[var] = Some(positive);
                changed = true;
            }
        }

        if all_satisfied {
            return true;
        }

        if !changed {
            break;
        }
    }

    // Check current state
    let mut all_satisfied = true;
    for clause in clauses {
        let mut satisfied = false;
        let mut has_unset = false;

        for &(var, positive) in clause {
            if let Some(val) = assignment[var] {
                if val == positive {
                    satisfied = true;
                    break;
                }
            } else {
                has_unset = true;
            }
        }

        if !satisfied {
            if !has_unset {
                return false;
            }
            all_satisfied = false;
        }
    }

    if all_satisfied {
        return true;
    }

    // Pick an unassigned variable
    let var = match assignment.iter().position(|a| a.is_none()) {
        Some(v) => v,
        None => return false,
    };

    // Try true
    let saved: Vec<Option<bool>> = assignment.clone();
    assignment[var] = Some(true);
    if dpll_inner(clauses, assignment) {
        return true;
    }

    // Try false
    *assignment = saved;
    assignment[var] = Some(false);
    dpll_inner(clauses, assignment)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_formula() {
        let cnf = CnfFormula::new();
        assert!(cnf.is_satisfiable());
    }

    #[test]
    fn test_single_var() {
        let mut cnf = CnfFormula::new();
        let v = cnf.get_or_create_var("a");
        cnf.add_clause(vec![(v, true)]);
        assert!(cnf.is_satisfiable());
    }

    #[test]
    fn test_contradiction() {
        let mut cnf = CnfFormula::new();
        let v = cnf.get_or_create_var("a");
        cnf.add_clause(vec![(v, true)]);
        cnf.add_clause(vec![(v, false)]);
        assert!(!cnf.is_satisfiable());
    }

    #[test]
    fn test_nand() {
        let mut cnf = CnfFormula::new();
        let a = cnf.get_or_create_var("a");
        let b = cnf.get_or_create_var("b");
        // NAND: ~a | ~b
        cnf.add_clause(vec![(a, false), (b, false)]);
        // Both must be true
        cnf.add_clause(vec![(a, true)]);
        cnf.add_clause(vec![(b, true)]);
        assert!(!cnf.is_satisfiable());
    }

    #[test]
    fn test_nand_one_true() {
        let mut cnf = CnfFormula::new();
        let a = cnf.get_or_create_var("a");
        let b = cnf.get_or_create_var("b");
        cnf.add_clause(vec![(a, false), (b, false)]);
        cnf.add_clause(vec![(a, true)]);
        // b can be false, so satisfiable
        assert!(cnf.is_satisfiable());
    }

    #[test]
    fn test_expr_and() {
        let mut cnf = CnfFormula::new();
        let a = cnf.get_or_create_var("a");
        let b = cnf.get_or_create_var("b");
        let expr = Expr::And(vec![Expr::Var(a), Expr::Var(b)]);
        cnf.add_expr(&expr);
        assert!(cnf.is_satisfiable());
    }

    #[test]
    fn test_expr_contradiction() {
        let mut cnf = CnfFormula::new();
        let a = cnf.get_or_create_var("a");
        let expr = Expr::And(vec![Expr::Var(a), Expr::Not(Box::new(Expr::Var(a)))]);
        cnf.add_expr(&expr);
        assert!(!cnf.is_satisfiable());
    }

    #[test]
    fn test_expr_or() {
        let mut cnf = CnfFormula::new();
        let a = cnf.get_or_create_var("a");
        let b = cnf.get_or_create_var("b");
        // a must be false
        cnf.add_clause(vec![(a, false)]);
        // a OR b must be true
        let expr = Expr::Or(vec![Expr::Var(a), Expr::Var(b)]);
        cnf.add_expr(&expr);
        // b must be true to satisfy
        assert!(cnf.is_satisfiable());
    }

    #[test]
    fn test_implies_via_cnf() {
        // Test: A => B (equivalent to ~A | B)
        let mut cnf = CnfFormula::new();
        let a = cnf.get_or_create_var("a");
        let b = cnf.get_or_create_var("b");
        // A is true
        cnf.add_clause(vec![(a, true)]);
        // A => B
        cnf.add_clause(vec![(a, false), (b, true)]);
        // NOT B
        cnf.add_clause(vec![(b, false)]);
        // Should be unsatisfiable (A=true, A=>B, ~B is contradiction)
        assert!(!cnf.is_satisfiable());
    }
}
