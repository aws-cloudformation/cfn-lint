use std::collections::HashSet;
use std::sync::LazyLock;

use regex::Regex;

use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

static SUB_VAR_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\$\{([^}]+)\}").unwrap());

pub struct W2001;

impl CfnLintRule for W2001 {
    fn id(&self) -> &str {
        "W2001"
    }
    fn short_description(&self) -> &str {
        "Unused parameter"
    }
    fn description(&self) -> &str {
        "Check for parameters that are defined but not referenced via Ref or Fn::Sub"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let params_node = root.get("Parameters").and_then(|n| n.as_object());
        let param_names: Vec<String> = match &params_node {
            Some(obj) => obj.keys().map(|s| s.to_string()).collect(),
            None => return vec![],
        };

        if param_names.is_empty() {
            return vec![];
        }

        // Skip when template has transforms — transforms may use parameters
        if root.get("Transform").is_some() {
            return vec![];
        }

        // Walk ALL sections including Parameters for Ref/Sub usage
        let referenced = collect_referenced_params(root, &[]);

        param_names
            .iter()
            .filter(|name| !referenced.contains(*name))
            .map(|name| {
                let pos = params_node
                    .and_then(|p| p.get(name.as_str()))
                    .map(|n| n.span().clone())
                    .unwrap_or_default();
                ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!("Parameter '{}' is defined but not used", name),
                    path: vec!["Parameters".to_string(), name.clone()],
                    span: pos,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }
            })
            .collect()
    }
}

/// Extract `${VarName}` references from an Fn::Sub template string.
/// Returns variable names found in `${...}` placeholders.
fn extract_sub_vars(template_str: &str) -> HashSet<String> {
    SUB_VAR_RE
        .captures_iter(template_str)
        .map(|cap| cap[1].trim().to_string())
        .collect()
}

/// Collect parameter names referenced via Ref, Fn::Sub, or Condition in the given AST.
fn collect_referenced_params(node: &AstNode, path: &[String]) -> HashSet<String> {
    let mut referenced = HashSet::new();

    ast::walk(node, path, &mut |n, _path| {
        if let AstNode::Function(func) = n {
            match func.name.as_str() {
                "Ref" => {
                    if let Some(name) = func.args.as_str() {
                        referenced.insert(name.to_string());
                    }
                }
                "Condition" => {
                    // Condition references a condition name, not a parameter — skip
                }
                "Fn::Sub" => {
                    match func.args.as_ref() {
                        // String form: !Sub '${Param}'
                        AstNode::String(s) => {
                            referenced.extend(extract_sub_vars(&s.value));
                        }
                        // Array form: !Sub ['${Param}', {LocalVar: value}]
                        AstNode::Array(arr) if arr.elements.len() == 2 => {
                            if let Some(tmpl_str) = arr.elements[0].as_str() {
                                let mut vars = extract_sub_vars(tmpl_str);
                                // Remove local substitution keys — they shadow parameters
                                if let Some(obj) = arr.elements[1].as_object() {
                                    for key in obj.keys() {
                                        vars.remove(key);
                                    }
                                }
                                referenced.extend(vars);
                            }
                        }
                        _ => {}
                    }
                    // Don't recurse into Fn::Sub args via walk — we handled it here.
                    // But walk will still descend into the args (the array elements / map values),
                    // which is fine — it may find nested Ref/Sub inside the substitution map values.
                }
                _ => {}
            }
        }
        true
    });

    referenced
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_used_parameter_via_ref() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Env
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_unused_parameter() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W2001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("W2001"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("W2001"));
        assert!(issues[0].message.contains("Env"));
    }

    #[test]
    fn test_no_parameters() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_used_parameter_via_sub_string() {
        let yaml = br#"
Parameters:
  BucketName:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketName}-suffix'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_sub_array_form_with_local_var() {
        // LocalAlias is a local substitution, not a parameter reference.
        // BucketName IS a parameter reference (not in the local map).
        let yaml = br#"
Parameters:
  BucketName:
    Type: String
  Unused:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub:
          - '${BucketName}-${LocalAlias}'
          - LocalAlias: my-value
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W2001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("Unused"));
    }

    #[test]
    fn test_sub_array_form_local_var_shadows_param() {
        // Even though ParamName is a parameter, the local substitution map
        // overrides it, so it should NOT count as a parameter reference.
        let yaml = br#"
Parameters:
  ParamName:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub:
          - '${ParamName}'
          - ParamName: hardcoded-value
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W2001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("ParamName"));
    }

    #[test]
    fn test_sub_multiple_vars() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
  App:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${Env}-${App}-bucket'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_condition_does_not_count_as_param_usage() {
        // Condition function references a condition name, not a parameter.
        let yaml = br#"
Parameters:
  Env:
    Type: String
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Env
      - prod
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::If:
          - IsProd
          - prod-bucket
          - dev-bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        // Env is used via Ref in the Conditions section, so it should be fine
        assert!(W2001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_nested_ref_in_sub_array_map_value() {
        // The substitution map value uses !Ref OtherParam, which should count.
        let yaml = br#"
Parameters:
  BucketName:
    Type: String
  OtherParam:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub:
          - '${BucketName}-${LocalVar}'
          - LocalVar: !Ref OtherParam
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        // Both BucketName (via Sub) and OtherParam (via Ref in map value) are used
        assert!(W2001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_extract_sub_vars() {
        let vars = extract_sub_vars("${Foo}-${Bar}-literal-${Baz}");
        assert_eq!(vars.len(), 3);
        assert!(vars.contains("Foo"));
        assert!(vars.contains("Bar"));
        assert!(vars.contains("Baz"));
    }

    #[test]
    fn test_extract_sub_vars_empty() {
        let vars = extract_sub_vars("no-variables-here");
        assert!(vars.is_empty());
    }

    #[test]
    fn test_extract_sub_vars_with_getatt() {
        // ${Resource.Attribute} is a GetAtt-style reference, not a parameter
        let vars = extract_sub_vars("${MyBucket.Arn}-${ParamName}");
        assert_eq!(vars.len(), 2);
        assert!(vars.contains("MyBucket.Arn"));
        assert!(vars.contains("ParamName"));
    }
}

crate::register_cfn_lint_rule!(W2001);
