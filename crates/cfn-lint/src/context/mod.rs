
use std::collections::HashMap;
use std::sync::Arc;

use crate::ast::{AstNode, NullNode, Span, StringNode};
use crate::conditions::Conditions as SatConditions;
use crate::template::Template;

/// Scenario produced when resolving a Ref.
pub struct RefScenario {
    pub value: AstNode,
    pub context: Context,
}

/// Scenario produced when evaluating a condition.
pub struct ConditionScenario {
    pub value: bool,
    pub context: Context,
}

/// Options for evolving a context. `None` fields keep the parent value.
#[derive(Default)]
pub struct ContextOptions {
    pub path: Option<Vec<String>>,
    pub cfn_path: Option<Vec<String>>,
    pub ref_values: Option<HashMap<String, AstNode>>,
    pub condition_state: Option<HashMap<String, bool>>,
    pub regions: Option<Vec<String>>,
    pub functions: Option<Vec<String>>,
}

/// Mutable validation state that evolves as we traverse the template.
/// The `Template` is shared via `Arc` and never cloned.
#[derive(Clone)]
pub struct Context {
    pub template: Arc<Template>,
    pub path: Vec<String>,
    /// Type-based path for keyword rule dispatch (e.g. ["Resources", "AWS::EC2::Instance", "Properties"]).
    pub cfn_path: Vec<String>,
    pub ref_values: HashMap<String, AstNode>,
    pub condition_state: HashMap<String, bool>,
    pub regions: Vec<String>,
    /// Supported intrinsic functions at this point in the template.
    /// None = all functions allowed. Some([]) = no functions allowed.
    pub functions: Option<Vec<String>>,
    /// SAT solver for condition satisfiability checks.
    pub sat_conditions: Option<Arc<SatConditions>>,
}

impl Context {
    pub fn new(template: Arc<Template>) -> Self {
        Context {
            template,
            path: Vec::new(),
            cfn_path: Vec::new(),
            ref_values: HashMap::new(),
            condition_state: HashMap::new(),
            regions: vec!["us-east-1".to_string()],
            functions: None,
            sat_conditions: None,
        }
    }

    pub fn empty() -> Self {
        use crate::ast::{AstNode, ObjectNode, Span};
        let empty_root = AstNode::Object(ObjectNode { entries: vec![], span: Span::default() });
        let tmpl = Template::from_ast(&empty_root).unwrap_or_else(|_| Template {
            root: empty_root,
            parameters: HashMap::new(),
            resources: HashMap::new(),
            conditions: HashMap::new(),
            mappings: HashMap::new(),
            outputs: HashMap::new(),
            description: None,
            version: None,
            filename: None,
        });
        Context {
            template: Arc::new(tmpl),
            path: Vec::new(),
            cfn_path: Vec::new(),
            ref_values: HashMap::new(),
            condition_state: HashMap::new(),
            regions: vec![],
            functions: None,
            sat_conditions: None,
        }
    }

    /// Create a new context with selective overrides.
    pub fn evolve(&self, opts: ContextOptions) -> Context {
        Context {
            template: Arc::clone(&self.template),
            path: opts.path.unwrap_or_else(|| self.path.clone()),
            cfn_path: opts.cfn_path.unwrap_or_else(|| self.cfn_path.clone()),
            ref_values: opts.ref_values.unwrap_or_else(|| self.ref_values.clone()),
            condition_state: opts
                .condition_state
                .unwrap_or_else(|| self.condition_state.clone()),
            regions: opts.regions.unwrap_or_else(|| self.regions.clone()),
            functions: if opts.functions.is_some() { opts.functions } else { self.functions.clone() },
            sat_conditions: self.sat_conditions.clone(),
        }
    }

    /// Resolve an AWS pseudo-parameter by name.
    pub fn resolve_pseudo_parameter(&self, name: &str) -> Option<AstNode> {
        let value = match name {
            "AWS::Region" => self.regions.first()?.clone(),
            "AWS::AccountId" => "123456789012".to_string(),
            "AWS::Partition" => "aws".to_string(),
            "AWS::URLSuffix" => "amazonaws.com".to_string(),
            "AWS::NoValue" => {
                return Some(AstNode::Null(NullNode {
                    span: Span::default(),
                }))
            }
            _ => return None,
        };
        Some(AstNode::String(StringNode {
            value,
            span: Span::default(),
        }))
    }

    /// Resolve a Ref to one or more scenarios.
    ///
    /// Resolution order: pseudo-parameters → already-resolved refs →
    /// template parameters (expanding AllowedValues) → resources.
    pub fn resolve_ref(&self, name: &str) -> Vec<RefScenario> {
        // 1. Pseudo-parameters
        if let Some(value) = self.resolve_pseudo_parameter(name) {
            return vec![RefScenario {
                value,
                context: self.clone(),
            }];
        }

        // 2. Already-resolved ref values
        if let Some(value) = self.ref_values.get(name) {
            return vec![RefScenario {
                value: value.clone(),
                context: self.clone(),
            }];
        }

        // 3. Template parameters
        if let Some(param) = self.template.parameters.get(name) {
            // Don't resolve List-type parameters — their Default is a comma-delimited
            // string but the runtime value is an array. We can't represent that.
            // Don't resolve SSM parameter types — their Default is the SSM path,
            // not the actual value that will be resolved at deploy time.
            if param.param_type.starts_with("List<")
                || param.param_type == "CommaDelimitedList"
                || param.param_type.contains("List<")
                || param.param_type.starts_with("AWS::SSM::Parameter")
            {
                return vec![];
            }
            if let Some(allowed) = &param.allowed_values {
                // One scenario per allowed value, pinning the ref in each
                return allowed
                    .iter()
                    .map(|v| {
                        let mut new_refs = self.ref_values.clone();
                        new_refs.insert(name.to_string(), v.clone());
                        RefScenario {
                            value: v.clone(),
                            context: self.evolve(ContextOptions {
                                ref_values: Some(new_refs),
                                ..Default::default()
                            }),
                        }
                    })
                    .collect();
            }
            // Parameter with a default but no AllowedValues
            if let Some(default) = &param.default {
                return vec![RefScenario {
                    value: default.clone(),
                    context: self.clone(),
                }];
            }
            // Parameter exists but we can't resolve it
            return vec![];
        }

        // 4. Resources — Ref to a resource returns a resource-type-specific value
        // (ARN, physical ID, etc.) that we can't determine statically. Don't resolve.
        vec![]
    }

    /// Evaluate a condition. If already resolved, return that single scenario.
    /// Tries to evaluate the condition expression before falling back to both scenarios.
    pub fn evaluate_condition(&self, name: &str) -> Vec<ConditionScenario> {
        if let Some(&value) = self.condition_state.get(name) {
            return vec![ConditionScenario {
                value,
                context: self.clone(),
            }];
        }

        // Try to evaluate the condition's AST node
        if let Some(condition_node) = self.template.conditions.get(name) {
            let condition_node = condition_node.clone();
            if let Some(result) = self.try_evaluate(&condition_node) {
                let mut ctx = self.clone();
                ctx.condition_state.insert(name.to_string(), result);
                return vec![ConditionScenario {
                    value: result,
                    context: ctx,
                }];
            }
        }

        // Can't resolve — return satisfiable branches (use SAT solver to prune)
        let mut true_state = self.condition_state.clone();
        true_state.insert(name.to_string(), true);
        let mut false_state = self.condition_state.clone();
        false_state.insert(name.to_string(), false);

        let mut scenarios = Vec::new();

        if self.sat_conditions.as_ref()
            .map(|sat| sat.is_condition_set_satisfiable(&true_state))
            .unwrap_or(true)
        {
            scenarios.push(ConditionScenario {
                value: true,
                context: self.evolve(ContextOptions {
                    condition_state: Some(true_state),
                    ..Default::default()
                }),
            });
        }

        if self.sat_conditions.as_ref()
            .map(|sat| sat.is_condition_set_satisfiable(&false_state))
            .unwrap_or(true)
        {
            scenarios.push(ConditionScenario {
                value: false,
                context: self.evolve(ContextOptions {
                    condition_state: Some(false_state),
                    ..Default::default()
                }),
            });
        }

        if scenarios.is_empty() {
            scenarios.push(ConditionScenario {
                value: true,
                context: self.evolve(ContextOptions {
                    condition_state: Some(self.condition_state.clone()),
                    ..Default::default()
                }),
            });
        }

        scenarios
    }

    /// Check if a condition assignment is satisfiable given current state.
    /// Uses the SAT solver if available.
    pub fn is_condition_satisfiable(&self, name: &str, value: bool) -> bool {
        if let Some(sat) = &self.sat_conditions {
            let mut state = self.condition_state.clone();
            state.insert(name.to_string(), value);
            sat.is_condition_set_satisfiable(&state)
        } else {
            true
        }
    }

    /// Try to resolve a node to a concrete value without a full Resolver.
    /// Handles Ref to pseudo-params and ref_values, and passes through literals.
    pub fn resolve_value(&self, node: &AstNode) -> Option<AstNode> {
        match node {
            AstNode::Function(func) if func.name == "Ref" => {
                let name = func.args.as_str()?;
                if let Some(v) = self.resolve_pseudo_parameter(name) {
                    return Some(v);
                }
                self.ref_values.get(name).cloned()
            }
            AstNode::Function(_) => None,
            other => Some(other.clone()),
        }
    }

    /// Try to evaluate a condition expression to a boolean.
    /// Returns None if the expression cannot be fully determined.
    ///
    /// Handles condition functions (parsed as single-key objects):
    /// - `Fn::Equals`: compare two resolved values
    /// - `Fn::Not`: negate inner condition
    /// - `Fn::And`: all conditions must be true
    /// - `Fn::Or`: any condition must be true
    /// - `Condition` (parsed as Function): look up in condition_state
    pub fn try_evaluate(&self, node: &AstNode) -> Option<bool> {
        match node {
            AstNode::Function(func) => {
                match func.name.as_str() {
                    "Condition" => {
                        let name = func.args.as_str()?;
                        self.condition_state.get(name).copied()
                    }
                    "Fn::Equals" => {
                        let arr = func.args.as_array()?;
                        if arr.elements.len() != 2 {
                            return None;
                        }
                        let left = self.resolve_value(&arr.elements[0])?;
                        let right = self.resolve_value(&arr.elements[1])?;
                        Some(ast_values_equal(&left, &right))
                    }
                    "Fn::Not" => {
                        let arr = func.args.as_array()?;
                        if arr.elements.len() != 1 {
                            return None;
                        }
                        self.try_evaluate(&arr.elements[0]).map(|v| !v)
                    }
                    "Fn::And" => {
                        let arr = func.args.as_array()?;
                        let mut has_unknown = false;
                        for elem in &arr.elements {
                            match self.try_evaluate(elem) {
                                Some(false) => return Some(false),
                                None => has_unknown = true,
                                Some(true) => {}
                            }
                        }
                        if has_unknown { None } else { Some(true) }
                    }
                    "Fn::Or" => {
                        let arr = func.args.as_array()?;
                        let mut has_unknown = false;
                        for elem in &arr.elements {
                            match self.try_evaluate(elem) {
                                Some(true) => return Some(true),
                                None => has_unknown = true,
                                Some(false) => {}
                            }
                        }
                        if has_unknown { None } else { Some(false) }
                    }
                    _ => None,
                }
            }
            // Fallback for raw object form (e.g., from serde_json deserialization)
            AstNode::Object(obj) if obj.len() == 1 => {
                let (key, value) = obj.iter().next()?;
                match key {
                    "Fn::Equals" => {
                        let arr = value.as_array()?;
                        if arr.elements.len() != 2 {
                            return None;
                        }
                        let left = self.resolve_value(&arr.elements[0])?;
                        let right = self.resolve_value(&arr.elements[1])?;
                        Some(ast_values_equal(&left, &right))
                    }
                    "Fn::Not" => {
                        let arr = value.as_array()?;
                        if arr.elements.len() != 1 {
                            return None;
                        }
                        self.try_evaluate(&arr.elements[0]).map(|v| !v)
                    }
                    "Fn::And" => {
                        let arr = value.as_array()?;
                        let mut has_unknown = false;
                        for elem in &arr.elements {
                            match self.try_evaluate(elem) {
                                Some(false) => return Some(false),
                                None => has_unknown = true,
                                Some(true) => {}
                            }
                        }
                        if has_unknown { None } else { Some(true) }
                    }
                    "Fn::Or" => {
                        let arr = value.as_array()?;
                        let mut has_unknown = false;
                        for elem in &arr.elements {
                            match self.try_evaluate(elem) {
                                Some(true) => return Some(true),
                                None => has_unknown = true,
                                Some(false) => {}
                            }
                        }
                        if has_unknown { None } else { Some(false) }
                    }
                    "Condition" => {
                        let name = value.as_str()?;
                        self.condition_state.get(name).copied()
                    }
                    _ => None,
                }
            }
            _ => None,
        }
    }
}

/// Compare two resolved AstNode values for equality (string comparison semantics).
fn ast_to_cfn_string(node: &AstNode) -> Option<String> {
    match node {
        AstNode::String(s) => Some(s.value.clone()),
        AstNode::Number(n) => Some(n.value.to_string()),
        AstNode::Bool(b) => Some(if b.value { "true" } else { "false" }.to_string()),
        _ => None,
    }
}

fn ast_values_equal(a: &AstNode, b: &AstNode) -> bool {
    match (ast_to_cfn_string(a), ast_to_cfn_string(b)) {
        (Some(a_str), Some(b_str)) => a_str == b_str,
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    fn make_template(yaml: &[u8]) -> Arc<Template> {
        let ast = parser::parse(yaml).unwrap();
        Arc::new(Template::from_ast(&ast).unwrap())
    }

    fn empty_template() -> Arc<Template> {
        make_template(b"AWSTemplateFormatVersion: '2010-09-09'\n")
    }

    #[test]
    fn test_new_defaults() {
        let ctx = Context::new(empty_template());
        assert!(ctx.path.is_empty());
        assert!(ctx.ref_values.is_empty());
        assert!(ctx.condition_state.is_empty());
        assert_eq!(ctx.regions, vec!["us-east-1"]);
    }

    #[test]
    fn test_evolve_preserves_template_arc() {
        let tmpl = empty_template();
        let ctx = Context::new(Arc::clone(&tmpl));
        let evolved = ctx.evolve(ContextOptions {
            path: Some(vec!["Resources".into(), "MyBucket".into()]),
            ..Default::default()
        });

        assert!(Arc::ptr_eq(&ctx.template, &evolved.template));
        assert_eq!(evolved.path, vec!["Resources", "MyBucket"]);
        // Unchanged fields carried over
        assert_eq!(evolved.regions, vec!["us-east-1"]);
        assert!(evolved.ref_values.is_empty());
    }

    #[test]
    fn test_evolve_overrides_all_fields() {
        let ctx = Context::new(empty_template());
        let mut refs = HashMap::new();
        refs.insert(
            "Env".into(),
            AstNode::String(StringNode {
                value: "prod".into(),
                span: Span::default(),
            }),
        );
        let mut conds = HashMap::new();
        conds.insert("IsProd".into(), true);

        let evolved = ctx.evolve(ContextOptions {
            path: Some(vec!["Outputs".into()]),
            ref_values: Some(refs),
            condition_state: Some(conds),
            regions: Some(vec!["eu-west-1".into()]),
            ..Default::default()
        });

        assert_eq!(evolved.path, vec!["Outputs"]);
        assert_eq!(
            evolved.ref_values.get("Env").unwrap().as_str(),
            Some("prod")
        );
        assert_eq!(evolved.condition_state.get("IsProd"), Some(&true));
        assert_eq!(evolved.regions, vec!["eu-west-1"]);
    }

    #[test]
    fn test_resolve_pseudo_params() {
        let ctx = Context::new(empty_template());

        let region = ctx.resolve_pseudo_parameter("AWS::Region").unwrap();
        assert_eq!(region.as_str(), Some("us-east-1"));

        let acct = ctx.resolve_pseudo_parameter("AWS::AccountId").unwrap();
        assert_eq!(acct.as_str(), Some("123456789012"));

        let part = ctx.resolve_pseudo_parameter("AWS::Partition").unwrap();
        assert_eq!(part.as_str(), Some("aws"));

        let suffix = ctx.resolve_pseudo_parameter("AWS::URLSuffix").unwrap();
        assert_eq!(suffix.as_str(), Some("amazonaws.com"));

        let no_val = ctx.resolve_pseudo_parameter("AWS::NoValue").unwrap();
        assert!(matches!(no_val, AstNode::Null(_)));

        assert!(ctx.resolve_pseudo_parameter("AWS::StackName").is_none());
        assert!(ctx.resolve_pseudo_parameter("NotAPseudo").is_none());
    }

    #[test]
    fn test_resolve_pseudo_region_uses_context_region() {
        let ctx = Context::new(empty_template()).evolve(ContextOptions {
            regions: Some(vec!["ap-southeast-1".into()]),
            ..Default::default()
        });
        let region = ctx.resolve_pseudo_parameter("AWS::Region").unwrap();
        assert_eq!(region.as_str(), Some("ap-southeast-1"));
    }

    #[test]
    fn test_resolve_ref_pseudo() {
        let ctx = Context::new(empty_template());
        let scenarios = ctx.resolve_ref("AWS::Region");
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].value.as_str(), Some("us-east-1"));
    }

    #[test]
    fn test_resolve_ref_from_ref_values() {
        let mut ctx = Context::new(empty_template());
        ctx.ref_values.insert(
            "MyParam".into(),
            AstNode::String(StringNode {
                value: "hello".into(),
                span: Span::default(),
            }),
        );
        let scenarios = ctx.resolve_ref("MyParam");
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].value.as_str(), Some("hello"));
    }

    #[test]
    fn test_resolve_ref_parameter_with_allowed_values() {
        let tmpl = make_template(
            br#"
Parameters:
  Env:
    Type: String
    AllowedValues:
      - dev
      - staging
      - prod
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let ctx = Context::new(tmpl);
        let scenarios = ctx.resolve_ref("Env");
        assert_eq!(scenarios.len(), 3);

        let values: Vec<&str> = scenarios.iter().filter_map(|s| s.value.as_str()).collect();
        assert_eq!(values, vec!["dev", "staging", "prod"]);

        // Each scenario pins the ref value in its context
        for s in &scenarios {
            assert!(s.context.ref_values.contains_key("Env"));
        }
    }

    #[test]
    fn test_resolve_ref_parameter_with_default_only() {
        let tmpl = make_template(
            br#"
Parameters:
  Env:
    Type: String
    Default: dev
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let ctx = Context::new(tmpl);
        let scenarios = ctx.resolve_ref("Env");
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].value.as_str(), Some("dev"));
    }

    #[test]
    fn test_resolve_ref_parameter_no_default_no_allowed() {
        let tmpl = make_template(
            br#"
Parameters:
  Env:
    Type: String
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let ctx = Context::new(tmpl);
        let scenarios = ctx.resolve_ref("Env");
        assert!(scenarios.is_empty());
    }

    #[test]
    fn test_resolve_ref_resource() {
        let tmpl = make_template(
            br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
"#,
        );
        let ctx = Context::new(tmpl);
        let scenarios = ctx.resolve_ref("MyBucket");
        // Ref to a resource returns a resource-type-specific value we can't determine
        assert_eq!(scenarios.len(), 0);
    }

    #[test]
    fn test_resolve_ref_unknown() {
        let ctx = Context::new(empty_template());
        let scenarios = ctx.resolve_ref("DoesNotExist");
        assert!(scenarios.is_empty());
    }

    #[test]
    fn test_evaluate_condition_already_resolved() {
        let mut ctx = Context::new(empty_template());
        ctx.condition_state.insert("IsProd".into(), true);

        let scenarios = ctx.evaluate_condition("IsProd");
        assert_eq!(scenarios.len(), 1);
        assert!(scenarios[0].value);
    }

    #[test]
    fn test_evaluate_condition_unknown_returns_both() {
        let ctx = Context::new(empty_template());
        let scenarios = ctx.evaluate_condition("IsProd");
        assert_eq!(scenarios.len(), 2);

        let (true_s, false_s) = if scenarios[0].value {
            (&scenarios[0], &scenarios[1])
        } else {
            (&scenarios[1], &scenarios[0])
        };

        assert!(true_s.value);
        assert!(!false_s.value);

        // Each scenario pins the condition in its context
        assert_eq!(true_s.context.condition_state.get("IsProd"), Some(&true));
        assert_eq!(false_s.context.condition_state.get("IsProd"), Some(&false));

        // Template Arc is shared
        assert!(Arc::ptr_eq(
            &true_s.context.template,
            &false_s.context.template
        ));
    }

    #[test]
    fn test_resolve_ref_priority_pseudo_over_parameter() {
        // Even if a parameter is named AWS::Region, pseudo wins
        let tmpl = make_template(
            br#"
Parameters:
  "AWS::Region":
    Type: String
    Default: override
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let ctx = Context::new(tmpl);
        let scenarios = ctx.resolve_ref("AWS::Region");
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].value.as_str(), Some("us-east-1"));
    }

    #[test]
    fn test_resolve_ref_priority_ref_values_over_parameter() {
        let tmpl = make_template(
            br#"
Parameters:
  Env:
    Type: String
    AllowedValues:
      - dev
      - prod
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let mut ctx = Context::new(tmpl);
        ctx.ref_values.insert(
            "Env".into(),
            AstNode::String(StringNode {
                value: "staging".into(),
                span: Span::default(),
            }),
        );

        let scenarios = ctx.resolve_ref("Env");
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].value.as_str(), Some("staging"));
    }

    // ── Condition satisfiability tests ──

    use crate::ast::{ArrayNode, FunctionNode, ObjectEntry, ObjectNode};
    use indexmap::IndexMap;

    /// Helper: build an Fn::Equals object node (parsed as single-key object).
    fn make_equals(left: AstNode, right: AstNode) -> AstNode {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Fn::Equals".to_string(), span: Span::default() }),
            key: "Fn::Equals".to_string(),
            value: AstNode::Array(ArrayNode {
                elements: vec![left, right],
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         })
    }

    /// Helper: build an Fn::Not object node.
    fn make_not(inner: AstNode) -> AstNode {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Fn::Not".to_string(), span: Span::default() }),
            key: "Fn::Not".to_string(),
            value: AstNode::Array(ArrayNode {
                elements: vec![inner],
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         })
    }

    /// Helper: build an Fn::And object node.
    fn make_and(conditions: Vec<AstNode>) -> AstNode {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Fn::And".to_string(), span: Span::default() }),
            key: "Fn::And".to_string(),
            value: AstNode::Array(ArrayNode {
                elements: conditions,
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         })
    }

    /// Helper: build an Fn::Or object node.
    fn make_or(conditions: Vec<AstNode>) -> AstNode {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Fn::Or".to_string(), span: Span::default() }),
            key: "Fn::Or".to_string(),
            value: AstNode::Array(ArrayNode {
                elements: conditions,
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         })
    }

    /// Helper: build a Condition reference as object (how it appears in condition expressions).
    fn make_condition_ref_obj(name: &str) -> AstNode {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Condition".to_string(), span: Span::default() }),
            key: "Condition".to_string(),
            value: AstNode::String(StringNode {
                value: name.to_string(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         })
    }

    fn str_node(s: &str) -> AstNode {
        AstNode::String(StringNode {
            value: s.to_string(),
            span: Span::default(),
        })
    }

    #[test]
    fn test_try_evaluate_equals_matching_strings() {
        let ctx = Context::new(empty_template());
        let node = make_equals(str_node("prod"), str_node("prod"));
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_equals_non_matching_strings() {
        let ctx = Context::new(empty_template());
        let node = make_equals(str_node("prod"), str_node("dev"));
        assert_eq!(ctx.try_evaluate(&node), Some(false));
    }

    #[test]
    fn test_try_evaluate_equals_with_ref_resolved() {
        let mut ctx = Context::new(empty_template());
        ctx.ref_values.insert("Env".into(), str_node("prod"));

        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Env")),
            span: Span::default(),
        });
        let node = make_equals(ref_node, str_node("prod"));
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_equals_with_unresolvable_ref() {
        let ctx = Context::new(empty_template());
        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Unknown")),
            span: Span::default(),
        });
        let node = make_equals(ref_node, str_node("prod"));
        assert_eq!(ctx.try_evaluate(&node), None);
    }

    #[test]
    fn test_try_evaluate_not_true() {
        let ctx = Context::new(empty_template());
        let inner = make_equals(str_node("a"), str_node("a"));
        let node = make_not(inner);
        assert_eq!(ctx.try_evaluate(&node), Some(false));
    }

    #[test]
    fn test_try_evaluate_not_false() {
        let ctx = Context::new(empty_template());
        let inner = make_equals(str_node("a"), str_node("b"));
        let node = make_not(inner);
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_not_unknown() {
        let ctx = Context::new(empty_template());
        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Unknown")),
            span: Span::default(),
        });
        let inner = make_equals(ref_node, str_node("x"));
        let node = make_not(inner);
        assert_eq!(ctx.try_evaluate(&node), None);
    }

    #[test]
    fn test_try_evaluate_and_all_true() {
        let ctx = Context::new(empty_template());
        let node = make_and(vec![
            make_equals(str_node("a"), str_node("a")),
            make_equals(str_node("b"), str_node("b")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_and_one_false() {
        let ctx = Context::new(empty_template());
        let node = make_and(vec![
            make_equals(str_node("a"), str_node("a")),
            make_equals(str_node("a"), str_node("b")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), Some(false));
    }

    #[test]
    fn test_try_evaluate_and_short_circuit_false() {
        // First is false, second is unknown — should still return false
        let ctx = Context::new(empty_template());
        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Unknown")),
            span: Span::default(),
        });
        let node = make_and(vec![
            make_equals(str_node("a"), str_node("b")),
            make_equals(ref_node, str_node("x")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), Some(false));
    }

    #[test]
    fn test_try_evaluate_and_unknown_blocks() {
        // First is true, second is unknown — can't determine
        let ctx = Context::new(empty_template());
        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Unknown")),
            span: Span::default(),
        });
        let node = make_and(vec![
            make_equals(str_node("a"), str_node("a")),
            make_equals(ref_node, str_node("x")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), None);
    }

    #[test]
    fn test_try_evaluate_or_one_true() {
        let ctx = Context::new(empty_template());
        let node = make_or(vec![
            make_equals(str_node("a"), str_node("b")),
            make_equals(str_node("a"), str_node("a")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_or_all_false() {
        let ctx = Context::new(empty_template());
        let node = make_or(vec![
            make_equals(str_node("a"), str_node("b")),
            make_equals(str_node("c"), str_node("d")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), Some(false));
    }

    #[test]
    fn test_try_evaluate_or_short_circuit_true() {
        // First is true, second is unknown — should still return true
        let ctx = Context::new(empty_template());
        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Unknown")),
            span: Span::default(),
        });
        let node = make_or(vec![
            make_equals(str_node("a"), str_node("a")),
            make_equals(ref_node, str_node("x")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_or_unknown_blocks() {
        // First is false, second is unknown — can't determine
        let ctx = Context::new(empty_template());
        let ref_node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("Unknown")),
            span: Span::default(),
        });
        let node = make_or(vec![
            make_equals(str_node("a"), str_node("b")),
            make_equals(ref_node, str_node("x")),
        ]);
        assert_eq!(ctx.try_evaluate(&node), None);
    }

    #[test]
    fn test_try_evaluate_condition_ref_resolved() {
        let mut ctx = Context::new(empty_template());
        ctx.condition_state.insert("IsProd".into(), true);
        let node = make_condition_ref_obj("IsProd");
        assert_eq!(ctx.try_evaluate(&node), Some(true));
    }

    #[test]
    fn test_try_evaluate_condition_ref_unresolved() {
        let ctx = Context::new(empty_template());
        let node = make_condition_ref_obj("IsProd");
        assert_eq!(ctx.try_evaluate(&node), None);
    }

    #[test]
    fn test_try_evaluate_condition_function_node() {
        // Condition as AstNode::Function (how it appears in Fn::If context)
        let mut ctx = Context::new(empty_template());
        ctx.condition_state.insert("IsProd".into(), false);
        let node = AstNode::Function(FunctionNode {
            name: "Condition".to_string(),
            args: Box::new(str_node("IsProd")),
            span: Span::default(),
        });
        assert_eq!(ctx.try_evaluate(&node), Some(false));
    }

    #[test]
    fn test_evaluate_condition_resolves_via_try_evaluate() {
        // Template with Fn::Equals condition, and ref_values providing the parameter
        let tmpl = make_template(
            br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Environment
      - prod
Parameters:
  Environment:
    Type: String
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let mut ctx = Context::new(tmpl);
        ctx.ref_values.insert("Environment".into(), str_node("prod"));

        let scenarios = ctx.evaluate_condition("IsProd");
        // try_evaluate resolves Fn::Equals to true (Environment == "prod")
        assert_eq!(scenarios.len(), 1);
        assert!(scenarios[0].value);
    }

    #[test]
    fn test_evaluate_condition_resolves_false() {
        let tmpl = make_template(
            br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Environment
      - prod
Parameters:
  Environment:
    Type: String
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let mut ctx = Context::new(tmpl);
        ctx.ref_values.insert("Environment".into(), str_node("dev"));

        let scenarios = ctx.evaluate_condition("IsProd");
        // try_evaluate resolves Fn::Equals to false (Environment == "dev" != "prod")
        assert_eq!(scenarios.len(), 1);
        assert!(!scenarios[0].value);
    }

    #[test]
    fn test_evaluate_condition_falls_back_to_both() {
        // No ref_values provided, so Fn::Equals can't resolve
        let tmpl = make_template(
            br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Environment
      - prod
Parameters:
  Environment:
    Type: String
Resources:
  Dummy:
    Type: AWS::SNS::Topic
"#,
        );
        let ctx = Context::new(tmpl);
        let scenarios = ctx.evaluate_condition("IsProd");
        assert_eq!(scenarios.len(), 2);
    }

    #[test]
    fn test_resolve_value_literal_passthrough() {
        let ctx = Context::new(empty_template());
        let node = str_node("hello");
        let result = ctx.resolve_value(&node).unwrap();
        assert_eq!(result.as_str(), Some("hello"));
    }

    #[test]
    fn test_resolve_value_ref_pseudo() {
        let ctx = Context::new(empty_template());
        let node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("AWS::Region")),
            span: Span::default(),
        });
        let result = ctx.resolve_value(&node).unwrap();
        assert_eq!(result.as_str(), Some("us-east-1"));
    }

    #[test]
    fn test_resolve_value_ref_from_ref_values() {
        let mut ctx = Context::new(empty_template());
        ctx.ref_values.insert("MyParam".into(), str_node("val"));
        let node = AstNode::Function(FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(str_node("MyParam")),
            span: Span::default(),
        });
        let result = ctx.resolve_value(&node).unwrap();
        assert_eq!(result.as_str(), Some("val"));
    }

    #[test]
    fn test_resolve_value_non_ref_function_returns_none() {
        let ctx = Context::new(empty_template());
        let node = AstNode::Function(FunctionNode {
            name: "Fn::Sub".to_string(),
            args: Box::new(str_node("something")),
            span: Span::default(),
        });
        assert!(ctx.resolve_value(&node).is_none());
    }
}
