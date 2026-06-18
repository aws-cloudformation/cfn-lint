// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

//! SAT-solver for CloudFormation Conditions.
//!
//! Mirrors Python's `cfnlint.conditions` package.

pub mod condition;
pub mod equals;
pub(crate) mod sat;

use std::collections::HashMap;

use condition::ConditionNamed;
use equals::Equal;
use sat::{CnfFormula, Expr};

use crate::template::Template;

/// Error when satisfaction cannot be determined.
#[derive(Debug, Clone)]
pub struct UnknownSatisfaction {
    pub message: String,
}

impl std::fmt::Display for UnknownSatisfaction {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for UnknownSatisfaction {}

/// Template-level conditions with SAT-solver.
/// Built once from the template, shared via Arc during validation.
#[derive(Debug, Clone)]
pub struct Conditions {
    conditions: HashMap<String, ConditionNamed>,
    cnf: CnfFormula,
    solver_params: HashMap<String, usize>,
    static_equals: HashMap<String, bool>,
    max_scenarios: usize,
}

impl Conditions {
    /// Build from a parsed Template.
    pub fn from_template(template: &Template) -> Self {
        let mut conditions: HashMap<String, ConditionNamed> = HashMap::new();

        for (k, _) in &template.conditions {
            match ConditionNamed::new(k, &template.conditions) {
                Ok(c) => { conditions.insert(k.clone(), c); }
                Err(_) => {
                    // Condition uses unsupported functions or malformed structure —
                    // excluded from SAT model (becomes unconstrained)
                }
            }
        }

        let condition_names: Vec<String> = conditions.keys().cloned().collect();
        let (cnf, solver_params, static_equals) = build_cnf(&conditions, template, &condition_names);

        Self { conditions, cnf, solver_params, static_equals, max_scenarios: 128 }
    }

    pub fn get(&self, name: &str) -> Option<&ConditionNamed> {
        self.conditions.get(name)
    }

    /// Check if a set of condition true/false assignments is satisfiable
    /// using the CNF formula directly.
    pub fn is_condition_set_satisfiable(&self, conditions: &HashMap<String, bool>) -> bool {
        let mut cnf = self.cnf.clone();
        for (name, &val) in conditions {
            if let Some(cond) = self.conditions.get(name) {
                let expr = cond.build_expr(&self.solver_params, &self.static_equals);
                if val {
                    cnf.add_expr(&expr);
                } else {
                    cnf.add_expr(&Expr::Not(Box::new(expr)));
                }
            }
        }
        cnf.is_satisfiable()
    }

    /// Check if the given scenario implies a condition is true.
    pub fn check_implies(&self, scenarios: &HashMap<String, bool>, implies: &str) -> bool {
        if let Some(&val) = scenarios.get(implies) {
            if !val { return false; }
        }

        let implies_cond = match self.conditions.get(implies) {
            Some(c) => c,
            None => return true,
        };

        let mut cnf = self.cnf.clone();
        for (name, &opt) in scenarios {
            if let Some(cond) = self.conditions.get(name) {
                let expr = cond.build_expr(&self.solver_params, &self.static_equals);
                if opt {
                    cnf.add_expr(&expr);
                } else {
                    cnf.add_expr(&Expr::Not(Box::new(expr)));
                }
            }
        }

        // If scenarios AND NOT(implies) is unsatisfiable, then scenarios => implies
        cnf.add_expr(&Expr::Not(Box::new(implies_cond.build_expr(&self.solver_params, &self.static_equals))));
        !cnf.is_satisfiable()
    }

    /// Build satisfiable scenarios for a set of conditions.
    pub fn build_scenarios(
        &self,
        conditions: &HashMap<String, std::collections::HashSet<bool>>,
    ) -> Vec<HashMap<String, bool>> {
        if conditions.is_empty() { return vec![]; }

        let mut base_cnf = self.cnf.clone();
        let mut fixed: HashMap<String, bool> = HashMap::new();
        let mut variable_names: Vec<String> = Vec::new();

        for (name, values) in conditions {
            if let Some(cond) = self.conditions.get(name) {
                if *values == [true].into() {
                    base_cnf.add_expr(&cond.build_expr(&self.solver_params, &self.static_equals));
                    fixed.insert(name.clone(), true);
                } else if *values == [false].into() {
                    base_cnf.add_expr(&Expr::Not(Box::new(cond.build_expr(&self.solver_params, &self.static_equals))));
                    fixed.insert(name.clone(), false);
                } else {
                    variable_names.push(name.clone());
                }
            }
        }

        let mut results = Vec::new();
        let n = variable_names.len();
        let max = std::cmp::min(1usize << n, self.max_scenarios);

        for i in 0..max {
            let mut cnf = base_cnf.clone();
            let mut params: HashMap<String, bool> = HashMap::new();

            for (j, name) in variable_names.iter().enumerate() {
                let val = (i >> (n - 1 - j)) & 1 == 0;
                params.insert(name.clone(), val);
                if let Some(cond) = self.conditions.get(name) {
                    let expr = cond.build_expr(&self.solver_params, &self.static_equals);
                    if val {
                        cnf.add_expr(&expr);
                    } else {
                        cnf.add_expr(&Expr::Not(Box::new(expr)));
                    }
                }
            }

            if cnf.is_satisfiable() {
                params.extend(fixed.clone());
                results.push(params);
            }
        }

        results
    }

    /// Check satisfiability with parameter values (for Rules section support).
    pub fn satisfiable(
        &self,
        conditions: &HashMap<String, bool>,
        parameter_values: &HashMap<String, String>,
    ) -> Result<bool, UnknownSatisfaction> {
        if conditions.is_empty() {
            return Ok(self.cnf.is_satisfiable());
        }

        let mut cnf = self.cnf.clone();
        let mut at_least_one_param_found = false;

        for (condition_name, &opt) in conditions {
            let cond = match self.conditions.get(condition_name) {
                Some(c) => c,
                None => return Err(UnknownSatisfaction {
                    message: format!("Can't resolve satisfaction for {condition_name:?}"),
                }),
            };

            for c_equals in cond.equals() {
                let mut found_params: Option<(String, String)> = None;

                for (param, value) in parameter_values {
                    let rh = equals::ref_hash(param);

                    for c_equal_param in c_equals.parameters() {
                        if !c_equal_param.satisfiable {
                            return Err(UnknownSatisfaction {
                                message: format!("Can't resolve satisfaction for {condition_name:?}"),
                            });
                        }
                    }

                    if c_equals.has_parameter_hash(&rh) {
                        found_params = Some((rh, value.clone()));
                    }
                }

                if let Some((matched_hash, value)) = found_params {
                    at_least_one_param_found = true;
                    let var = cnf.get_or_create_var(&c_equals.hash);
                    if c_equals.test_with_hash(&matched_hash, &value) {
                        cnf.add_clause(vec![(var, true)]);
                    } else {
                        cnf.add_clause(vec![(var, false)]);
                    }

                    let cond_expr = cond.build_expr(&self.solver_params, &self.static_equals);
                    if opt {
                        cnf.add_expr(&cond_expr);
                    } else {
                        cnf.add_expr(&Expr::Not(Box::new(cond_expr)));
                    }
                }
            }
        }

        if !at_least_one_param_found {
            return Ok(self.cnf.is_satisfiable());
        }

        Ok(cnf.is_satisfiable())
    }
}

/// Build the CNF formula from conditions and template parameters.
fn build_cnf(
    conditions: &HashMap<String, ConditionNamed>,
    template: &Template,
    condition_names: &[String],
) -> (CnfFormula, HashMap<String, usize>, HashMap<String, bool>) {
    let mut cnf = CnfFormula::new();
    let mut equal_vars: HashMap<String, Option<bool>> = HashMap::new();
    let mut equals_map: HashMap<String, Equal> = HashMap::new();

    for name in condition_names {
        if let Some(cond) = conditions.get(name) {
            for eq in cond.equals() {
                if equal_vars.contains_key(&eq.hash) { continue; }

                // Python treats all Equals as opaque symbols in the SAT solver,
                // even static ones. Always create a variable.
                equal_vars.insert(eq.hash.clone(), None);
                cnf.get_or_create_var(&eq.hash);

                // NAND: two equals sharing a parameter can't both be true
                for (e_hash, e_eq) in &equals_map {
                    for param in eq.parameters() {
                        for e_param in e_eq.parameters() {
                            if param.hash == e_param.hash {
                                let v1 = cnf.get_or_create_var(&eq.hash);
                                let v2 = cnf.get_or_create_var(e_hash);
                                cnf.add_clause(vec![(v1, false), (v2, false)]);
                            }
                        }
                    }
                }
                equals_map.insert(eq.hash.clone(), eq.clone());
            }
        }
    }

    // AllowedValues constraints from template parameters
    let mut allowed_values: HashMap<String, Vec<String>> = HashMap::new();
    for (param_name, param) in &template.parameters {
        if let Some(ref av) = param.allowed_values {
            let rh = equals::ref_hash(param_name);
            let hashes: Vec<String> = av.iter()
                .map(|v| equals::get_hash(v))
                .collect();
            allowed_values.insert(rh, hashes);
        }
    }

    if !allowed_values.is_empty() {
        // Remove used values
        for (_, eq) in &equals_map {
            for param in eq.parameters() {
                if let Some(av) = allowed_values.get_mut(&param.hash) {
                    if let Some(static_hash) = eq.static_value_hash() {
                        if let Some(pos) = av.iter().position(|x| x == &static_hash) {
                            av.remove(pos);
                        } else {
                            equal_vars.insert(eq.hash.clone(), Some(false));
                        }
                    }
                }
            }
        }

        // If all allowed values covered, at least one equals must be true
        for (allowed_hash, remaining) in &allowed_values {
            if remaining.is_empty() {
                let mut relevant_vars = Vec::new();
                for (_, eq) in &equals_map {
                    for param in eq.parameters() {
                        if &param.hash == allowed_hash {
                            let var = cnf.get_or_create_var(&eq.hash);
                            relevant_vars.push((var, true));
                        }
                    }
                }
                if !relevant_vars.is_empty() {
                    cnf.add_clause(relevant_vars);
                }
            }
        }
    }

    let solver_params: HashMap<String, usize> = equal_vars.iter()
        .filter_map(|(hash, static_val)| {
            if static_val.is_none() {
                Some((hash.clone(), cnf.get_or_create_var(hash)))
            } else {
                None
            }
        })
        .collect();

    let static_equals: HashMap<String, bool> = equal_vars.iter()
        .filter_map(|(hash, static_val)| {
            static_val.map(|v| (hash.clone(), v))
        })
        .collect();

    (cnf, solver_params, static_equals)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    fn make_template(yaml: &[u8]) -> Template {
        let ast = parser::parse(yaml).unwrap();
        Template::from_ast(&ast).unwrap()
    }

    #[test]
    fn test_basic_condition_parsing() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        assert!(c.get("IsProd").is_some());
    }

    #[test]
    fn test_satisfiable_empty() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
Parameters:
  Env:
    Type: String
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        assert!(c.satisfiable(&HashMap::new(), &HashMap::new()).unwrap());
    }

    #[test]
    fn test_check_implies_true() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
  IsProdOrStaging:
    Fn::Or:
      - Condition: IsProd
      - Fn::Equals:
          - !Ref Env
          - staging
Parameters:
  Env:
    Type: String
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        let mut scenarios = HashMap::new();
        scenarios.insert("IsProd".to_string(), true);
        assert!(c.check_implies(&scenarios, "IsProdOrStaging"));
    }

    #[test]
    fn test_check_implies_false_in_scenarios() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
Parameters:
  Env:
    Type: String
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        let mut scenarios = HashMap::new();
        scenarios.insert("IsProd".to_string(), false);
        assert!(!c.check_implies(&scenarios, "IsProd"));
    }

    #[test]
    fn test_static_equals() {
        let t = make_template(br#"
Conditions:
  AlwaysTrue:
    Fn::Equals: ["a", "a"]
  AlwaysFalse:
    Fn::Equals: ["a", "b"]
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        let scenarios = HashMap::new();
        // Python's SAT solver treats all Equals as opaque symbols,
        // so it can't determine static truth values via check_implies.
        // Both are satisfiable in either direction.
        assert!(!c.check_implies(&scenarios, "AlwaysTrue"));
        assert!(!c.check_implies(&scenarios, "AlwaysFalse"));
    }

    #[test]
    fn test_not_condition() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
  IsNotProd:
    Fn::Not:
      - Condition: IsProd
Parameters:
  Env:
    Type: String
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        let mut scenarios = HashMap::new();
        scenarios.insert("IsProd".to_string(), false);
        assert!(c.check_implies(&scenarios, "IsNotProd"));
    }

    #[test]
    fn test_mutual_exclusion_with_allowed_values() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
  IsDev:
    Fn::Equals:
      - !Ref Env
      - dev
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        let mut scenarios = HashMap::new();
        scenarios.insert("IsProd".to_string(), true);
        assert!(!c.check_implies(&scenarios, "IsDev"));
    }

    #[test]
    fn test_build_scenarios() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
  IsUsEast1:
    Fn::Equals:
      - !Ref "AWS::Region"
      - us-east-1
Parameters:
  Env:
    Type: String
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);
        let mut conds = HashMap::new();
        conds.insert("IsProd".to_string(), [true, false].into());
        conds.insert("IsUsEast1".to_string(), [true, false].into());
        let scenarios = c.build_scenarios(&conds);
        assert!(!scenarios.is_empty());
        assert!(scenarios.len() <= 4);
    }

    #[test]
    fn test_is_condition_set_satisfiable() {
        let t = make_template(br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
  IsDev:
    Fn::Equals:
      - !Ref Env
      - dev
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);

        // IsProd=true alone is fine
        let mut s = HashMap::new();
        s.insert("IsProd".to_string(), true);
        assert!(c.is_condition_set_satisfiable(&s));

        // IsProd=true AND IsDev=true is not satisfiable (mutual exclusion)
        s.insert("IsDev".to_string(), true);
        assert!(!c.is_condition_set_satisfiable(&s));
    }

    #[test]
    fn test_single_condition_both_branches_satisfiable() {
        let t = make_template(br#"
Conditions:
  MultiAZ:
    Fn::Equals:
      - !Ref pMultiAZ
      - true
Parameters:
  pMultiAZ:
    Type: String
    AllowedValues: [true, false]
Resources:
  D:
    Type: AWS::SNS::Topic
"#);
        let c = Conditions::from_template(&t);

        let mut s = HashMap::new();
        s.insert("MultiAZ".to_string(), true);
        assert!(c.is_condition_set_satisfiable(&s), "MultiAZ=true should be satisfiable");

        s.clear();
        s.insert("MultiAZ".to_string(), false);
        assert!(c.is_condition_set_satisfiable(&s), "MultiAZ=false should be satisfiable");
    }
}
