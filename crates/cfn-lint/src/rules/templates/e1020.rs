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

        // Walk the AST looking for Ref functions
        collect_ref_issues(
            root,
            &valid_refs,
            &module_prefixes,
            &condition_names,
            false,
            &mut issues,
        );
        issues
    }
}

fn collect_ref_issues(
    node: &AstNode,
    valid_refs: &[&str],
    module_prefixes: &[String],
    condition_names: &std::collections::HashSet<&str>,
    in_unknown_condition: bool,
    issues: &mut Vec<ValidationError>,
) {
    match node {
        AstNode::Function(func) if func.name == "Ref" => {
            if let Some(ref_name) = func.args.as_str() {
                // Skip Refs with dots (e.g. "Resource.Version" - SAM artifact)
                if ref_name.contains('.') {
                    return;
                }
                // Skip if inside an Fn::If with unknown condition
                if in_unknown_condition {
                    return;
                }
                let is_module_sub = module_prefixes
                    .iter()
                    .any(|p| ref_name.starts_with(p.as_str()));
                if !is_module_sub && valid_refs.binary_search(&ref_name).is_err() {
                    issues.push(ValidationError {
                        rule_id: Some("E1020".to_string()),
                        message: format!("'{}' is not one of {:?}", ref_name, valid_refs),
                        path: vec![],
                        span: func.span.clone(),
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
                issues,
            );
        }
        AstNode::Function(func) if func.name == "Fn::If" => {
            // Check if the condition name exists
            if let Some(arr) = func.args.as_array() {
                if arr.elements.len() >= 1 {
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
    use crate::ast::*;

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
}

crate::register_cfn_lint_rule!(E1020);
