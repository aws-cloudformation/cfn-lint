use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E3703: Validate CodePipeline action configuration.
/// TemplatePath must reference a valid InputArtifact, RoleArn must be valid format.
pub struct E3703;

impl CfnLintRule for E3703 {
    fn id(&self) -> &str { "E3703" }
    fn short_description(&self) -> &str { "Validate CodePipeline action configuration" }
    fn description(&self) -> &str {
        "Certain action types have configuration constraints such as \
         TemplatePath referencing a valid InputArtifact"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::CodePipeline::Pipeline" {
                continue;
            }
            let stages = match root
                .get("Resources").and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("Stages"))
                .and_then(|s| s.as_array())
            {
                Some(s) => s,
                None => continue,
            };

            for (si, stage) in stages.elements.iter().enumerate() {
                let actions = match stage.get("Actions").and_then(|a| a.as_array()) {
                    Some(a) => a,
                    None => continue,
                };
                for (ai, action) in actions.elements.iter().enumerate() {
                    let base_path = vec![
                        "Resources".into(), name.clone(), "Properties".into(),
                        "Stages".into(), si.to_string(), "Actions".into(), ai.to_string(),
                    ];

                    // Check TemplatePath references a valid InputArtifact
                    if let Some(template_path) = action
                        .get("Configuration")
                        .and_then(|c| c.get("TemplatePath"))
                        .and_then(|t| t.as_str())
                    {
                        let input_names: Vec<String> = action
                            .get("InputArtifacts")
                            .and_then(|i| i.as_array())
                            .map(|arr| {
                                arr.elements.iter()
                                    .filter_map(|e| e.get("Name").and_then(|n| n.as_str()))
                                    .map(String::from)
                                    .collect()
                            })
                            .unwrap_or_default();

                        let artifact_prefix = template_path.split("::").next().unwrap_or("");
                        if !input_names.iter().any(|n| n == artifact_prefix) {
                            let mut path = base_path.clone();
                            path.extend(["Configuration".into(), "TemplatePath".into()]);
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "'{}' is not one of {:?}",
                                    artifact_prefix, input_names
                                ),
                                path,
                                span: action.get("Configuration")
                                    .and_then(|c| c.get("TemplatePath"))
                                    .map(|n| n.span().clone())
                                    .unwrap_or_default(),
                                keyword: String::new(),
                                unknown: false,
                                resolved_from_ref: false,
                                context: vec![],
                                schema_id: None,
});
                        }
                    }

                    // Check RoleArn format
                    if let Some(role_arn) = action
                        .get("Configuration")
                        .and_then(|c| c.get("RoleArn"))
                        .and_then(|r| r.as_str())
                    {
                        if !role_arn.starts_with("arn:") || !role_arn.contains(":iam:") || !role_arn.contains(":role/") {
                            let mut path = base_path.clone();
                            path.extend(["Configuration".into(), "RoleArn".into()]);
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "'{}' is not a valid IAM Role ARN",
                                    role_arn
                                ),
                                path,
                                span: action.get("Configuration")
                                    .and_then(|c| c.get("RoleArn"))
                                    .map(|n| n.span().clone())
                                    .unwrap_or_default(),
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
        }
        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_template_path() {
        let yaml = br#"
Resources:
  Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      RoleArn: arn:aws:iam::123456789012:role/role
      Stages:
        - Name: Source
          Actions:
            - Name: S3Source
              ActionTypeId:
                Category: Source
                Owner: AWS
                Provider: S3
                Version: "1"
              OutputArtifacts:
                - Name: SourceOutput
        - Name: Deploy
          Actions:
            - Name: CfnDeploy
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: CloudFormation
                Version: "1"
              InputArtifacts:
                - Name: SourceOutput
              Configuration:
                TemplatePath: SourceOutput::template.yaml
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3703.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_invalid_template_path() {
        let yaml = br#"
Resources:
  Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      RoleArn: arn:aws:iam::123456789012:role/role
      Stages:
        - Name: Deploy
          Actions:
            - Name: CfnDeploy
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: CloudFormation
                Version: "1"
              InputArtifacts:
                - Name: SourceOutput
              Configuration:
                TemplatePath: BadArtifact::template.yaml
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3703.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("BadArtifact"));
        assert!(issues[0].message.contains("not one of"));
    }
}

crate::register_cfn_lint_rule!(E3703);
