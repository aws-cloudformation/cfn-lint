use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

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

pub struct E1020;

impl CfnLintRule for E1020 {
    fn id(&self) -> &str {
        "E1020"
    }

    fn short_description(&self) -> &str {
        "Ref validation of value"
    }

    fn description(&self) -> &str {
        "Validates Ref function value references a valid parameter, resource, or pseudo-parameter"
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
        // SAM templates create implicit resources we can't predict
        if crate::transform::is_sam_template(root) {
            return vec![];
        }
        let mut issues = Vec::new();
        // Build the set of valid ref targets
        let mut valid_refs: Vec<&str> = Vec::new();
        // Collect MODULE and Serverless resource names for prefix matching
        let mut module_prefixes: Vec<String> = Vec::new();
        for (name, resource) in &template.resources {
            valid_refs.push(name.as_str());
            if resource.resource_type.ends_with("::MODULE")
                || resource.resource_type.starts_with("AWS::Serverless::")
            {
                module_prefixes.push(name.clone());
            }
        }
        for name in template.parameters.keys() {
            valid_refs.push(name.as_str());
        }
        for p in PSEUDO_PARAMETERS {
            valid_refs.push(p);
        }
        valid_refs.sort_unstable();

        // Build set of valid condition names
        let condition_names: std::collections::HashSet<&str> =
            template.conditions.keys().map(|s| s.as_str()).collect();

        // Refs are validated everywhere, but a Ref that lives in an Output value
        // is attributed to E6101 (the Outputs-value rule) to match Python
        // cfn-lint, while Refs elsewhere are E1020. Walk the two regions with the
        // matching rule id; `Outputs` is handled separately from the rest of the
        // template so the rest keeps reporting E1020.
        if let Some(root_obj) = root.as_object() {
            for (section, node) in root_obj.iter() {
                let rule_id = if section == "Outputs" {
                    "E6101"
                } else {
                    "E1020"
                };
                collect_ref_issues(
                    node,
                    &valid_refs,
                    &module_prefixes,
                    &condition_names,
                    false,
                    rule_id,
                    &mut issues,
                );
            }
        }
        issues
    }
}

fn collect_ref_issues(
    node: &AstNode,
    valid_refs: &[&str],
    module_prefixes: &[String],
    condition_names: &std::collections::HashSet<&str>,
    in_unknown_condition: bool,
    rule_id: &str,
    issues: &mut Vec<ValidationError>,
) {
    match node {
        AstNode::Function(func) if func.name == "Ref" => {
            if let Some(ref_name) = func.args.as_str() {
                // Skip if inside an Fn::If with unknown condition
                if in_unknown_condition {
                    return;
                }
                // A dotted Ref (e.g. `Resource.Attr`) is only legitimate for a
                // MODULE/Serverless resource output; the `is_module_sub` prefix
                // check below covers that. Any other dotted Ref is genuinely
                // invalid and Python reports it, so it is NOT skipped here.
                let is_module_sub = module_prefixes
                    .iter()
                    .any(|p| ref_name.starts_with(p.as_str()));
                if !is_module_sub && valid_refs.binary_search(&ref_name).is_err() {
                    issues.push(ValidationError {
                        rule_id: Some(rule_id.to_string()),
                        message: format!("'{}' is not one of {:?}", ref_name, valid_refs),
                        path: vec![],
                        span: func.span,
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
            // Also walk args in case of nested functions
            collect_ref_issues(
                &func.args,
                valid_refs,
                module_prefixes,
                condition_names,
                in_unknown_condition,
                rule_id,
                issues,
            );
        }
        AstNode::Function(func) if func.name == "Fn::If" => {
            // Check if the condition name exists
            if let Some(arr) = func.args.as_array() {
                if !arr.elements.is_empty() {
                    let cond_name = arr.elements[0].as_str().unwrap_or("");
                    let cond_unknown = !condition_names.contains(cond_name);
                    // Walk branches with updated condition awareness
                    for elem in &arr.elements {
                        collect_ref_issues(
                            elem,
                            valid_refs,
                            module_prefixes,
                            condition_names,
                            in_unknown_condition || cond_unknown,
                            rule_id,
                            issues,
                        );
                    }
                    return;
                }
            }
            collect_ref_issues(
                &func.args,
                valid_refs,
                module_prefixes,
                condition_names,
                in_unknown_condition,
                rule_id,
                issues,
            );
        }
        AstNode::Function(func) => {
            collect_ref_issues(
                &func.args,
                valid_refs,
                module_prefixes,
                condition_names,
                in_unknown_condition,
                rule_id,
                issues,
            );
        }
        AstNode::Object(obj) => {
            for value in obj.values() {
                collect_ref_issues(
                    value,
                    valid_refs,
                    module_prefixes,
                    condition_names,
                    in_unknown_condition,
                    rule_id,
                    issues,
                );
            }
        }
        AstNode::Array(arr) => {
            for elem in &arr.elements {
                collect_ref_issues(
                    elem,
                    valid_refs,
                    module_prefixes,
                    condition_names,
                    in_unknown_condition,
                    rule_id,
                    issues,
                );
            }
        }
        _ => {}
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E1020.id(), "E1020");
        assert_eq!(E1020.short_description(), "Ref validation of value");
        assert_eq!(E1020.severity(), Severity::Error);
    }

    #[test]
    fn test_valid_ref_to_resource() {
        let yaml = r#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref MyBucket
"#;
        let ast = crate::parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1020.validate_template(&tmpl, &ast);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_valid_ref_to_parameter() {
        let yaml = r#"
Parameters:
  Env:
    Type: String
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Env
"#;
        let ast = crate::parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1020.validate_template(&tmpl, &ast);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_valid_ref_to_pseudo_parameter() {
        let yaml = r#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref AWS::Region
"#;
        let ast = crate::parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1020.validate_template(&tmpl, &ast);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_invalid_ref_target() {
        let yaml = r#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref DoesNotExist
"#;
        let ast = crate::parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1020.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1020"));
        assert!(issues[0].message.contains("DoesNotExist"));
    }

    // A Ref in an Output value is attributed to E6101 (the Outputs-value rule),
    // matching Python cfn-lint, while a Ref in a resource property is E1020.
    #[test]
    fn test_output_ref_is_e6101() {
        let yaml = r#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
Outputs:
  Out:
    Value: !Ref DoesNotExist
"#;
        let ast = crate::parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1020.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E6101"));
    }

    // A dotted Ref value (`Resource.Attr`) is invalid CloudFormation and is now
    // reported (previously skipped wholesale). In an Output it surfaces as E6101.
    #[test]
    fn test_dotted_ref_in_output_reported() {
        let yaml = r#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
Outputs:
  Out:
    Value: !Ref MyBucket.Arn
"#;
        let ast = crate::parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1020.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E6101"));
        assert!(issues[0].message.contains("MyBucket.Arn"));
    }
}

crate::register_cfn_lint_rule!(E1020);
