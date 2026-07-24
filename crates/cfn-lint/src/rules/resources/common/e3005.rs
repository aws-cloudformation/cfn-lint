use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3005;

impl CfnLintRule for E3005 {
    fn id(&self) -> &str {
        "E3005"
    }

    fn short_description(&self) -> &str {
        "Check DependsOn values for Resources"
    }

    fn description(&self) -> &str {
        "Validates DependsOn references exist and are available given conditions"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/DependsOn", "Resources/*/DependsOn/*"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Only validate string values (individual DependsOn entries)
        let dep_name = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        let mut resource_names: Vec<&str> =
            ctx.template.resources.keys().map(|s| s.as_str()).collect();

        // Determine the resource that owns this DependsOn by looking at the path
        // Path is like ["Resources", "MyResource", "DependsOn"] or ["Resources", "MyResource", "DependsOn", "0"]
        let owner_resource = if path.len() >= 2 {
            Some(path[1].as_str())
        } else {
            None
        };

        // A resource cannot depend on itself
        if let Some(owner) = owner_resource {
            resource_names.retain(|r| *r != owner);
        }

        if !resource_names.contains(&dep_name) {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!("{:?} is not one of {:?}", dep_name, resource_names),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        // Check conditional availability: is there a scenario where the owner
        // resource IS available but the target of the DependsOn is NOT? This
        // mirrors Python's `cfn.is_resource_available`, which constrains the
        // owner and target conditions *jointly* rather than testing the target
        // condition in isolation. The joint check matters when conditions share
        // structure: e.g. an owner gated on `Fn::Or [C1, C2]` that depends on a
        // resource gated on `C1`, where `C1` and `C2` are the *same* `Fn::Equals`
        // (identical hash => same SAT variable). There `owner-true AND C1-false`
        // is unsatisfiable, so the target is always present when the owner is —
        // no finding. Testing `C1-false` alone would spuriously flag it (E3005
        // false positive on SAM-transformed usage-plan output).
        let mut errors = Vec::new();
        let target_resource = ctx.template.resources.get(dep_name);
        if let Some(target) = target_resource {
            if let Some(target_condition) = &target.condition {
                let owner_condition = owner_resource
                    .and_then(|name| ctx.template.resources.get(name))
                    .and_then(|r| r.condition.as_ref());

                // If the owner is gated on the *same* condition as the target,
                // they are always present together — no finding. (Handled as a
                // fast path because a single condition constrained to both true
                // and false cannot be expressed as one satisfiability query.)
                let same_condition = owner_condition == Some(target_condition);

                // Scenario: owner available (its condition true, or always true
                // when it has none) AND target missing (its condition false).
                let mut scenario = std::collections::HashMap::new();
                if let Some(owner_cond) = owner_condition {
                    scenario.insert(owner_cond.clone(), true);
                }
                scenario.insert(target_condition.clone(), false);

                if !same_condition && ctx.are_conditions_satisfiable(&scenario) {
                    errors.push(ValidationError {
                        rule_id: None,
                        keyword: format!("cfnLint:{}", self.id()),
                        message: format!(
                            "{:?} will not exist when condition {:?} is false",
                            dep_name, target_condition
                        ),
                        path: path.to_vec(),
                        span: instance.span(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
        }

        errors
    }
}

#[cfg(test)]
mod tests {
    use crate::engine::Engine;
    use crate::parser;
    use crate::template::Template;

    fn e3005_messages(yaml: &[u8]) -> Vec<String> {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let mut engine = Engine::new();
        engine
            .validate(&tmpl, &ast, &["us-east-1".to_string()])
            .into_iter()
            .filter(|i| i.rule_id.as_deref() == Some("E3005"))
            .map(|i| i.message)
            .collect()
    }

    // Owner gated on `Fn::Or [C1, C2]` depends on a resource gated on `C1`,
    // where C1 and C2 are the *same* static `Fn::Equals` (identical hash =>
    // same SAT variable). `owner-true AND C1-false` reduces to `v AND NOT v`,
    // which is unsatisfiable, so the target is always present when the owner is.
    // Also covers the same-condition case (a resource gated on the shared
    // condition depending on another resource gated on the same condition).
    // Mirrors SAM's api_with_usageplans_shared_attributes_two output, on which
    // Python cfn-lint emits nothing. Regression guard against an E3005 false
    // positive.
    #[test]
    fn test_shared_or_condition_no_false_positive() {
        let yaml = br#"
Conditions:
  C1: {"Fn::Equals": ["test", "test"]}
  C2: {"Fn::Equals": ["test", "test"]}
  Shared: {"Fn::Or": [{"Condition": "C2"}, {"Condition": "C1"}]}
Resources:
  MyApiOne: {Type: AWS::SNS::Topic, Condition: C1}
  MyApiTwo: {Type: AWS::SNS::Topic, Condition: C2}
  Plan:
    Type: AWS::SNS::Topic
    Condition: Shared
    DependsOn: [MyApiOne, MyApiTwo]
  Key:
    Type: AWS::SNS::Topic
    Condition: Shared
    DependsOn: [Plan]
"#;
        let msgs = e3005_messages(yaml);
        assert!(msgs.is_empty(), "expected no E3005, got: {msgs:?}");
    }

    // An *unconditional* owner depends on resources gated on a condition that
    // can be false => the dependency may be absent while the owner exists.
    // Mirrors api_with_usageplans_shared_attributes_three, on which Python
    // cfn-lint DOES emit E3005. Regression guard against under-reporting.
    #[test]
    fn test_unconditional_owner_conditional_target_emits() {
        let yaml = br#"
Conditions:
  C1: {"Fn::Equals": ["test", "test"]}
  C2: {"Fn::Equals": ["test", "test"]}
Resources:
  MyApiOne: {Type: AWS::SNS::Topic, Condition: C1}
  MyApiTwo: {Type: AWS::SNS::Topic, Condition: C2}
  Plan:
    Type: AWS::SNS::Topic
    DependsOn: [MyApiOne, MyApiTwo]
"#;
        let msgs = e3005_messages(yaml);
        assert_eq!(msgs.len(), 2, "expected 2 E3005, got: {msgs:?}");
    }

    // A DependsOn naming a resource that does not exist is always reported.
    #[test]
    fn test_missing_dependency_reported() {
        let yaml = br#"
Resources:
  A:
    Type: AWS::SNS::Topic
    DependsOn: DoesNotExist
"#;
        let msgs = e3005_messages(yaml);
        assert_eq!(msgs.len(), 1, "expected 1 E3005, got: {msgs:?}");
    }
}

crate::register_cfn_lint_rule!(E3005);
