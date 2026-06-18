use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E3050: Check if REFing to an IAM resource with Path set.
/// Some resources don't support looking up IAM resources by name.
/// When a Ref is used and the Path is not '/', this is an error.
pub struct E3050;

impl CfnLintRule for E3050 {
    fn id(&self) -> &str {
        "E3050"
    }
    fn short_description(&self) -> &str {
        "Check if REFing to a IAM resource with path set"
    }
    fn description(&self) -> &str {
        "Some resources don't support looking up the IAM resource by name. \
         This check validates when a REF is being used and the Path is not '/'"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            let key = match RESOURCES_AND_KEYS
                .iter()
                .find(|(rt, _)| *rt == resource.resource_type)
            {
                Some((_, k)) => *k,
                None => continue,
            };

            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            let ref_target = match props.get(key).and_then(|n| n.as_function()) {
                Some(f) if f.name == "Ref" => f.args.as_str(),
                _ => continue,
            };

            let ref_target = match ref_target {
                Some(t) => t,
                None => continue,
            };

            // Check if the referenced resource has a Path property
            let iam_path = root
                .get("Resources")
                .and_then(|r| r.get(ref_target))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("Path"))
                .and_then(|n| n.as_str());

            if let Some(path_val) = iam_path {
                if path_val != "/" {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "When using a Ref to IAM resource the Path must be '/'. \
                             Switch to GetAtt if the Path has to be '{}'.",
                            path_val
                        ),
                        path: vec![
                            "Resources".to_string(),
                            name.to_string(),
                            "Properties".to_string(),
                            key.to_string(),
                        ],
                        span: props.get(key).unwrap().span().clone(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                }
            }
        }
        issues
    }
}

/// Resource types and the property key that references an IAM role.
const RESOURCES_AND_KEYS: &[(&str, &str)] = &[("AWS::CodeBuild::Project", "ServiceRole")];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_ref_with_default_path() {
        let yaml = br#"
Resources:
  Role:
    Type: AWS::IAM::Role
    Properties:
      Path: /
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement: []
  Project:
    Type: AWS::CodeBuild::Project
    Properties:
      ServiceRole: !Ref Role
      Source:
        Type: CODEPIPELINE
      Artifacts:
        Type: CODEPIPELINE
      Environment:
        ComputeType: BUILD_GENERAL1_SMALL
        Image: aws/codebuild/standard:1.0
        Type: LINUX_CONTAINER
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3050.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_ref_with_custom_path() {
        let yaml = br#"
Resources:
  Role:
    Type: AWS::IAM::Role
    Properties:
      Path: /custom/path/
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement: []
  Project:
    Type: AWS::CodeBuild::Project
    Properties:
      ServiceRole: !Ref Role
      Source:
        Type: CODEPIPELINE
      Artifacts:
        Type: CODEPIPELINE
      Environment:
        ComputeType: BUILD_GENERAL1_SMALL
        Image: aws/codebuild/standard:1.0
        Type: LINUX_CONTAINER
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3050.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3050"));
        assert!(issues[0].message.contains("/custom/path/"));
        assert!(issues[0].message.contains("GetAtt"));
    }
}

crate::register_cfn_lint_rule!(E3050);
