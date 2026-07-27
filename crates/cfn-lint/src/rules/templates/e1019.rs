use std::collections::HashSet;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E1019: Validate `Fn::Sub` variable references point to valid targets.
///
/// The schema pipeline's `fn_sub` keyword (jsonschema/keywords/fn_intrinsics.rs)
/// validates `${Var}` references, but only where schema-guided traversal reaches
/// the `Fn::Sub` — it does NOT descend into schemaless object properties (e.g. an
/// ApiGateway `Body`/OpenAPI blob typed `{"type": ["object","string"]}`). The
/// walker, by contrast, visits *every* node in the template and dispatches the
/// `Fn/Sub` keyword for each `Fn::Sub` it finds, at any depth.
///
/// This rule hooks that walker dispatch so `${Var}` references are checked
/// everywhere, matching Python cfn-lint (whose schema validator recurses into
/// schemaless objects by default). Overlap with the schema-pipeline findings on
/// schema-covered subs is collapsed by the E1019 span+message dedup in
/// `engine::validate`, so this only *adds* findings in regions the pipeline
/// cannot reach. The message format is kept byte-identical to the pipeline's so
/// that dedup matches.
pub struct E1019;

/// Pseudo-parameters that are always valid `Ref`/`Fn::Sub` targets.
const PSEUDO_PARAMETERS: &[&str] = &[
    "AWS::AccountId",
    "AWS::NoValue",
    "AWS::NotificationARNs",
    "AWS::Partition",
    "AWS::Region",
    "AWS::StackId",
    "AWS::StackName",
    "AWS::URLSuffix",
];

impl CfnLintRule for E1019 {
    fn id(&self) -> &str {
        "E1019"
    }

    fn short_description(&self) -> &str {
        "Fn::Sub variable references"
    }

    fn description(&self) -> &str {
        "Validate Fn::Sub variable references point to valid targets"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Fn/Sub"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let func = match instance.as_function() {
            Some(f) if f.name == "Fn::Sub" => f,
            _ => return vec![],
        };
        let ctx = match &validator.context {
            Some(c) => c,
            None => return vec![],
        };
        // Extension-schema / unresolvable contexts leave functions unvalidated
        // (mirrors the pipeline's fn_sub behaviour).
        if ctx.unresolvable_function_mode {
            return vec![];
        }

        let valid_refs: HashSet<&str> = ctx
            .template
            .parameters
            .keys()
            .map(|s| s.as_str())
            .chain(ctx.template.resources.keys().map(|s| s.as_str()))
            .chain(PSEUDO_PARAMETERS.iter().copied())
            .collect();

        // Extract the template string and any local variables (the second element
        // of the `[template, {vars}]` form).
        let (tmpl, local_vars): (&str, HashSet<&str>) = match func.args.as_ref() {
            AstNode::String(s) => (s.value.as_str(), HashSet::new()),
            AstNode::Array(arr) if arr.elements.len() == 2 => {
                let Some(s) = arr.elements[0].as_str() else {
                    return vec![];
                };
                let Some(map) = arr.elements[1].as_object() else {
                    return vec![];
                };
                // Bail out when a local-variable value is a `Ref` to a target that
                // does not exist. The value is unresolvable, so the schema pipeline
                // (and Python cfn-lint) leave the whole Fn::Sub unvalidated rather
                // than reporting its `${Var}` references — mirror that here to avoid
                // false positives on the remaining variables.
                let has_invalid_ref = map.values().any(|v| {
                    v.as_function()
                        .filter(|f| f.name == "Ref")
                        .and_then(|f| f.args.as_str())
                        .is_some_and(|r| !valid_refs.contains(r))
                });
                if has_invalid_ref {
                    return vec![];
                }
                (s, map.keys().collect())
            }
            _ => return vec![],
        };

        let mut errors = Vec::new();
        for var in extract_sub_variables(tmpl) {
            // Dotted `${Resource.Attr}` — validate the resource-name part.
            let name = var.split('.').next().unwrap_or("");
            if name.is_empty() || valid_refs.contains(name) || local_vars.contains(name) {
                continue;
            }
            let mut all: Vec<&str> = valid_refs
                .iter()
                .chain(local_vars.iter())
                .copied()
                .collect();
            all.sort();
            errors.push(ValidationError {
                rule_id: Some("E1019".to_string()),
                keyword: "fn_sub".to_string(),
                message: format!("'{name}' is not one of {all:?}"),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
        errors
    }
}

/// Extract `${Var}` references from an `Fn::Sub` template string, skipping the
/// literal-escape form `${!Literal}`. Mirrors the pipeline scanner so messages
/// (and therefore dedup) line up.
fn extract_sub_variables(tmpl: &str) -> Vec<&str> {
    let bytes = tmpl.as_bytes();
    let mut out = Vec::new();
    let mut i = 0;
    while i < bytes.len() {
        if i + 1 < bytes.len() && bytes[i] == b'$' && bytes[i + 1] == b'{' {
            if i + 2 < bytes.len() && bytes[i + 2] == b'!' {
                // ${!...} literal escape — skip to closing brace.
                i += 3;
                while i < bytes.len() && bytes[i] != b'}' {
                    i += 1;
                }
                i += 1;
                continue;
            }
            let start = i + 2;
            let mut end = start;
            while end < bytes.len() && bytes[end] != b'}' {
                end += 1;
            }
            let var = tmpl[start..end].trim();
            if !var.is_empty() {
                out.push(var);
            }
            i = end + 1;
        } else {
            i += 1;
        }
    }
    out
}

crate::register_cfn_lint_rule!(E1019);

#[cfg(test)]
mod tests {
    use crate::engine::Engine;
    use crate::parser;
    use crate::template::Template;

    fn e1019_count(yaml: &[u8]) -> usize {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let mut engine = Engine::new();
        engine
            .validate(&tmpl, &ast, &["us-east-1".to_string()])
            .iter()
            .filter(|i| i.rule_id.as_deref() == Some("E1019"))
            .count()
    }

    // The walker visits every node, so an `Fn::Sub` buried inside a schemaless
    // object property (no `properties` schema to guide descent — e.g. an
    // ApiGateway `Body`) still gets its `${Var}` references validated. This is
    // the gap the standalone stub used to miss.
    #[test]
    fn test_sub_in_schemaless_object_is_validated() {
        let yaml = br#"
Resources:
  Api:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Body:
        paths:
          /x:
            get:
              uri: !Sub "arn:${DifferentFunction.Arn}"
"#;
        assert_eq!(e1019_count(yaml), 1);
    }

    // When a Fn::Sub's local-variable map contains a `Ref` to an undefined
    // target, the value is unresolvable and the whole Fn::Sub is left
    // unvalidated (matches the schema pipeline / Python), so the remaining
    // `${Var}` references must NOT be flagged.
    #[test]
    fn test_sub_with_invalid_localvar_ref_bails() {
        let yaml = br#"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Sub:
          - "install ${myPackage} ${Package}"
          - myPackage: !Ref httpdPackage
"#;
        assert_eq!(e1019_count(yaml), 0);
    }

    // A local variable defined in the Fn::Sub map is a valid reference.
    #[test]
    fn test_sub_local_variable_is_valid() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub:
          - "${Prefix}-bucket"
          - Prefix: my
"#;
        assert_eq!(e1019_count(yaml), 0);
    }

    // A `${Var}` naming a real resource is valid; an unknown one is flagged.
    #[test]
    fn test_sub_resource_ref_valid_unknown_flagged() {
        let ok = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
  Topic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${Bucket}-topic"
"#;
        assert_eq!(e1019_count(ok), 0);
        let bad = br#"
Resources:
  Topic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub "${Nonexistent}-topic"
"#;
        assert_eq!(e1019_count(bad), 1);
    }
}
