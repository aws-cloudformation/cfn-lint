use crate::ast::AstNode;
use crate::helpers::SUB_VARIABLE_REGEX;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct W2010;

impl CfnLintRule for W2010 {
    fn id(&self) -> &str {
        "W2010"
    }
    fn short_description(&self) -> &str {
        "NoEcho parameters are not masked in Metadata and Outputs"
    }
    fn description(&self) -> &str {
        "Using NoEcho does not mask values stored in Metadata, Outputs, or Resource Metadata"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let no_echo_params: Vec<&str> = template
            .parameters
            .iter()
            .filter(|(_, p)| p.no_echo)
            .map(|(name, _)| name.as_str())
            .collect();

        if no_echo_params.is_empty() {
            return vec![];
        }

        let mut issues = Vec::new();

        // Check template-level Metadata section
        if let Some(metadata) = root.get("Metadata") {
            find_noecho_refs(
                metadata,
                &no_echo_params,
                &["Metadata"],
                "Metadata",
                &mut issues,
            );
        }

        // Check Outputs section
        if let Some(outputs) = root.get("Outputs") {
            find_noecho_refs(
                outputs,
                &no_echo_params,
                &["Outputs"],
                "Outputs",
                &mut issues,
            );
        }

        // Check Resource Metadata
        if let Some(resources) = root.get("Resources") {
            if let Some(res_obj) = resources.as_object() {
                for (res_name, res_node) in res_obj.iter() {
                    if let Some(meta) = res_node.get("Metadata") {
                        find_noecho_refs(
                            meta,
                            &no_echo_params,
                            &["Resources", res_name, "Metadata"],
                            "resource metadata",
                            &mut issues,
                        );
                    }
                }
            }
        }

        issues
    }
}

fn find_noecho_refs(
    node: &AstNode,
    no_echo_params: &[&str],
    path_prefix: &[&str],
    section_label: &str,
    issues: &mut Vec<ValidationError>,
) {
    let path: Vec<String> = path_prefix.iter().map(|s| s.to_string()).collect();
    find_refs_recursive(node, no_echo_params, &path, section_label, issues);
}

fn find_refs_recursive(
    node: &AstNode,
    no_echo_params: &[&str],
    path: &[String],
    section_label: &str,
    issues: &mut Vec<ValidationError>,
) {
    match node {
        AstNode::Function(func) => {
            if func.name == "Ref" {
                if let Some(param_name) = func.args.as_str() {
                    if no_echo_params.contains(&param_name) {
                        issues.push(ValidationError {
                            rule_id: Some("W2010".to_string()),
                            message: format!(
                                "Don't use 'NoEcho' parameter '{}' in {}",
                                param_name, section_label
                            ),
                            path: path.to_vec(),
                            span: func.span,
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }
            } else if func.name == "Fn::Sub" {
                // Check Fn::Sub template strings for ${NoEchoParam} references
                let template_str = match func.args.as_ref() {
                    AstNode::String(s) => Some(s.value.as_str()),
                    AstNode::Array(arr) if !arr.elements.is_empty() => arr.elements[0].as_str(),
                    _ => None,
                };
                // Collect local substitution keys to exclude
                let local_keys: Vec<&str> = if let Some(arr) = func.args.as_array() {
                    if arr.elements.len() == 2 {
                        arr.elements[1]
                            .as_object()
                            .map(|o| o.keys().collect())
                            .unwrap_or_default()
                    } else {
                        vec![]
                    }
                } else {
                    vec![]
                };
                if let Some(tmpl) = template_str {
                    for cap in SUB_VARIABLE_REGEX.captures_iter(tmpl) {
                        let var_name = cap[1].trim();
                        if var_name.contains('.') || local_keys.contains(&var_name) {
                            continue;
                        }
                        if no_echo_params.contains(&var_name) {
                            issues.push(ValidationError {
                                rule_id: Some("W2010".to_string()),
                                message: format!(
                                    "Don't use 'NoEcho' parameter '{}' in {}",
                                    var_name, section_label
                                ),
                                path: path.to_vec(),
                                span: func.span,
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
            // Recurse into function args
            find_refs_recursive(&func.args, no_echo_params, path, section_label, issues);
        }
        AstNode::Object(obj) => {
            for (key, val) in obj.iter() {
                let mut child_path = path.to_vec();
                child_path.push(key.to_string());
                find_refs_recursive(val, no_echo_params, &child_path, section_label, issues);
            }
        }
        AstNode::Array(arr) => {
            for (i, elem) in arr.elements.iter().enumerate() {
                let mut child_path = path.to_vec();
                child_path.push(i.to_string());
                find_refs_recursive(elem, no_echo_params, &child_path, section_label, issues);
            }
        }
        _ => {}
    }
}

crate::register_cfn_lint_rule!(W2010);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    // C58: after hoisting the regex to a static, Fn::Sub detection of a NoEcho
    // parameter in Outputs must still work.
    #[test]
    fn test_noecho_in_sub_output_flagged() {
        let yaml = br#"
Parameters:
  Secret:
    Type: String
    NoEcho: true
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  Leak:
    Value: !Sub "value-${Secret}"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W2010.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1, "got: {:?}", issues);
        assert!(issues[0].message.contains("Secret"));
    }

    #[test]
    fn test_noecho_direct_ref_in_output_flagged() {
        let yaml = br#"
Parameters:
  Secret:
    Type: String
    NoEcho: true
Outputs:
  Leak:
    Value: !Ref Secret
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W2010.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1, "got: {:?}", issues);
    }

    #[test]
    fn test_no_noecho_params_no_issue() {
        let yaml = br#"
Parameters:
  Public:
    Type: String
Outputs:
  Out:
    Value: !Ref Public
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2010.validate_template(&tmpl, &ast).is_empty());
    }
}
