use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3026;

/// A scenario is a map of condition_name → bool (true/false).
type Scenario = HashMap<String, bool>;

impl E3026 {
    /// Check if a ParameterGroup resource has cluster-enabled='yes'.
    /// The `cluster_enabled_node` may be a string or Fn::If.
    /// Returns list of (Option<Scenario>, is_cluster_enabled) pairs.
    fn get_cluster_scenarios(
        &self,
        pg_name: &str,
        root: &AstNode,
        parent_scenario: &Option<Scenario>,
    ) -> Vec<(Option<Scenario>, bool)> {
        let ce_node = match root
            .get("Resources")
            .and_then(|r| r.get(pg_name))
            .and_then(|r| r.get("Properties"))
            .and_then(|p| p.get("Properties"))
            .and_then(|p| p.get("cluster-enabled"))
        {
            Some(n) => n,
            None => return vec![],
        };

        if let Some(s) = ce_node.as_str() {
            let scenario = parent_scenario.clone();
            return vec![(scenario, s == "yes")];
        }

        if let Some(func) = ce_node.as_function() {
            if func.name == "Fn::If" {
                if let Some(arr) = func.args.as_array() {
                    if arr.elements.len() == 3 {
                        if let Some(cond_name) = arr.elements[0].as_str() {
                            // If parent_scenario already pins this condition, use that
                            if let Some(sc) = parent_scenario {
                                if let Some(&val) = sc.get(cond_name) {
                                    let branch = if val {
                                        &arr.elements[1]
                                    } else {
                                        &arr.elements[2]
                                    };
                                    let is_yes = branch.as_str() == Some("yes");
                                    return vec![(parent_scenario.clone(), is_yes)];
                                }
                            }
                            // Expand into two scenarios
                            let mut results = vec![];
                            for (branch_val, branch_node) in
                                [(true, &arr.elements[1]), (false, &arr.elements[2])]
                            {
                                let is_yes = branch_node.as_str() == Some("yes");
                                let mut sc = parent_scenario.clone().unwrap_or_default();
                                sc.insert(cond_name.to_string(), branch_val);
                                results.push((Some(sc), is_yes));
                            }
                            return results;
                        }
                    }
                }
            }
        }

        vec![]
    }

    /// Resolve a property value given a scenario. If the value is Fn::If and the
    /// scenario pins the condition, return the appropriate branch.
    fn resolve_with_scenario<'a>(
        &self,
        node: &'a AstNode,
        scenario: &Option<Scenario>,
    ) -> &'a AstNode {
        if let Some(func) = node.as_function() {
            if func.name == "Fn::If" {
                if let Some(arr) = func.args.as_array() {
                    if arr.elements.len() == 3 {
                        if let Some(cond_name) = arr.elements[0].as_str() {
                            if let Some(sc) = scenario {
                                if let Some(&val) = sc.get(cond_name) {
                                    return if val {
                                        &arr.elements[1]
                                    } else {
                                        &arr.elements[2]
                                    };
                                }
                            }
                        }
                    }
                }
            }
        }
        node
    }

    /// Extract Ref target resource names from CacheParameterGroupName.
    /// Returns (Option<Scenario>, ref_name) pairs.
    fn get_param_group_refs(&self, cpg_node: &AstNode) -> Vec<(Option<Scenario>, String)> {
        // Direct Ref
        if let Some(func) = cpg_node.as_function() {
            if func.name == "Ref" {
                if let Some(name) = func.args.as_str() {
                    return vec![(None, name.to_string())];
                }
            }
            // Fn::If
            if func.name == "Fn::If" {
                if let Some(arr) = func.args.as_array() {
                    if arr.elements.len() == 3 {
                        if let Some(cond_name) = arr.elements[0].as_str() {
                            let mut results = vec![];
                            for (branch_val, branch_node) in
                                [(true, &arr.elements[1]), (false, &arr.elements[2])]
                            {
                                if let Some(ref_func) = branch_node.as_function() {
                                    if ref_func.name == "Ref" {
                                        if let Some(name) = ref_func.args.as_str() {
                                            let mut sc = HashMap::new();
                                            sc.insert(cond_name.to_string(), branch_val);
                                            results.push((Some(sc), name.to_string()));
                                        }
                                    }
                                }
                            }
                            return results;
                        }
                    }
                }
            }
        }
        vec![]
    }

    fn scenario_text(scenario: &Scenario) -> String {
        scenario
            .iter()
            .map(|(k, v)| {
                format!(
                    "when condition \"{}\" is {}",
                    k,
                    if *v { "True" } else { "False" }
                )
            })
            .collect::<Vec<_>>()
            .join(" and ")
    }

    fn check_replication_group(
        &self,
        name: &str,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();

        let props = match root
            .get("Resources")
            .and_then(|r| r.get(name))
            .and_then(|r| r.get("Properties"))
        {
            Some(p) => p,
            None => return issues,
        };

        let cpg_node = match props.get("CacheParameterGroupName") {
            Some(n) => n,
            None => return issues,
        };

        let pg_refs = self.get_param_group_refs(cpg_node);

        for (ref_scenario, pg_name) in &pg_refs {
            // Verify it's actually a ParameterGroup resource
            let pg_res = match template.get_resource(pg_name) {
                Some(r) if r.resource_type == "AWS::ElastiCache::ParameterGroup" => r,
                _ => continue,
            };

            // Check if the parameter group's condition conflicts with the scenario
            if let Some(pg_condition) = &pg_res.condition {
                if let Some(sc) = ref_scenario {
                    if let Some(&val) = sc.get(pg_condition) {
                        if !val {
                            // The parameter group's condition is false in this scenario
                            continue;
                        }
                    }
                }
            }

            let cluster_scenarios = self.get_cluster_scenarios(pg_name, root, ref_scenario);

            for (scenario, is_cluster) in &cluster_scenarios {
                if !is_cluster {
                    continue;
                }

                // Check AutomaticFailoverEnabled
                if let Some(af_node) = props.get("AutomaticFailoverEnabled") {
                    let resolved = self.resolve_with_scenario(af_node, scenario);
                    if resolved.as_bool() == Some(false) {
                        let message = match scenario {
                            Some(sc) if !sc.is_empty() => format!(
                                "\"AutomaticFailoverEnabled\" must be misssing or True when setting up a cluster when {} at Resources/{}/Properties/AutomaticFailoverEnabled",
                                Self::scenario_text(sc), name
                            ),
                            _ => format!(
                                "\"AutomaticFailoverEnabled\" must be misssing or True when setting up a cluster at Resources/{}/Properties/AutomaticFailoverEnabled",
                                name
                            ),
                        };
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message,
                            path: vec![
                                "Resources".to_string(),
                                name.to_string(),
                                "Properties".to_string(),
                                "AutomaticFailoverEnabled".to_string(),
                            ],
                            span: af_node.span(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }

                // Check NumCacheClusters (only if NumNodeGroups is not truthy)
                let has_num_node_groups = if let Some(nng_node) = props.get("NumNodeGroups") {
                    let resolved = self.resolve_with_scenario(nng_node, scenario);
                    match resolved.as_f64() {
                        Some(v) => v != 0.0,
                        None => resolved.as_function().is_some(),
                    }
                } else {
                    false
                };

                if !has_num_node_groups {
                    let num_cache_clusters = props
                        .get("NumCacheClusters")
                        .map(|n| self.resolve_with_scenario(n, scenario))
                        .and_then(|n| n.as_f64())
                        .unwrap_or(0.0);

                    if num_cache_clusters <= 1.0 {
                        let ncc_span = props
                            .get("NumCacheClusters")
                            .map(|n| n.span())
                            .unwrap_or_else(|| props.span());

                        let message = match scenario {
                            Some(sc) if !sc.is_empty() => format!(
                                "\"NumCacheClusters\" must be greater than one when creating a cluster when {} at Resources/{}/Properties/NumCacheClusters",
                                Self::scenario_text(sc), name
                            ),
                            _ => format!(
                                "\"NumCacheClusters\" must be greater than one when creating a cluster at Resources/{}/Properties/NumCacheClusters",
                                name
                            ),
                        };
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message,
                            path: vec![
                                "Resources".to_string(),
                                name.to_string(),
                                "Properties".to_string(),
                                "NumCacheClusters".to_string(),
                            ],
                            span: ncc_span,
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

        issues
    }
}

impl CfnLintRule for E3026 {
    fn id(&self) -> &str {
        "E3026"
    }
    fn short_description(&self) -> &str {
        "Check Elastic Cache Redis Cluster settings"
    }
    fn description(&self) -> &str {
        "Validates ElastiCache Redis cluster failover settings"
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
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::ElastiCache::ReplicationGroup" {
                continue;
            }
            issues.extend(self.check_replication_group(name, template, root));
        }
        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_cluster_mode_with_failover_true() {
        let yaml = br#"
Resources:
  MyPG:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: test
      CacheParameterGroupFamily: redis3.2
      Properties:
        cluster-enabled: 'yes'
  Redis:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: test
      CacheParameterGroupName: !Ref MyPG
      AutomaticFailoverEnabled: true
      NumCacheClusters: 2
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3026.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_cluster_mode_with_failover_false() {
        let yaml = br#"
Resources:
  MyPG:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: test
      CacheParameterGroupFamily: redis3.2
      Properties:
        cluster-enabled: 'yes'
  Redis:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: test
      CacheParameterGroupName: !Ref MyPG
      AutomaticFailoverEnabled: false
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3026.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 2); // failover false + NumCacheClusters missing
        assert!(issues
            .iter()
            .any(|i| i.message.contains("AutomaticFailoverEnabled")));
        assert!(issues
            .iter()
            .any(|i| i.message.contains("NumCacheClusters")));
    }

    #[test]
    fn test_non_cluster_no_errors() {
        let yaml = br#"
Resources:
  MyPG:
    Type: AWS::ElastiCache::ParameterGroup
    Properties:
      Description: test
      CacheParameterGroupFamily: redis3.2
      Properties:
        cluster-enabled: 'no'
  Redis:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: test
      CacheParameterGroupName: !Ref MyPG
      AutomaticFailoverEnabled: false
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3026.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3026);
