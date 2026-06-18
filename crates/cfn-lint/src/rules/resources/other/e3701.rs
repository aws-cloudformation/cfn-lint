use std::collections::HashSet;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3701: Validate CodePipeline InputArtifacts reference previously defined OutputArtifacts,
/// and OutputArtifacts names are unique.
pub struct E3701;

impl CfnLintRule for E3701 {
    fn id(&self) -> &str {
        "E3701"
    }
    fn short_description(&self) -> &str {
        "Validate CodePipeline artifact names"
    }
    fn description(&self) -> &str {
        "InputArtifacts names must be previously defined OutputArtifact names, \
         and OutputArtifacts names must be unique"
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
            if resource.resource_type != "AWS::CodePipeline::Pipeline" {
                continue;
            }
            let stages = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("Stages"))
                .and_then(|s| s.as_array())
            {
                Some(s) => s,
                None => continue,
            };

            let mut output_names: HashSet<String> = HashSet::new();

            for (stage_idx, stage) in stages.elements.iter().enumerate() {
                let actions = match stage.get("Actions").and_then(|a| a.as_array()) {
                    Some(a) => a,
                    None => continue,
                };

                for (action_idx, action) in actions.elements.iter().enumerate() {
                    // Collect OutputArtifacts
                    if let Some(outputs) = action.get("OutputArtifacts").and_then(|o| o.as_array())
                    {
                        for (oa_idx, oa) in outputs.elements.iter().enumerate() {
                            if let Some(oa_name) = oa.get("Name").and_then(|n| n.as_str()) {
                                if !output_names.insert(oa_name.to_string()) {
                                    issues.push(ValidationError {
                                        rule_id: Some(self.id().to_string()),
                                        message: format!(
                                            "'{}' is already a defined 'OutputArtifact' Name",
                                            oa_name
                                        ),
                                        path: vec![
                                            "Resources".into(),
                                            name.clone(),
                                            "Properties".into(),
                                            "Stages".into(),
                                            stage_idx.to_string(),
                                            "Actions".into(),
                                            action_idx.to_string(),
                                            "OutputArtifacts".into(),
                                            oa_idx.to_string(),
                                            "Name".into(),
                                        ],
                                        span: oa
                                            .get("Name")
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

                    // Check InputArtifacts
                    if let Some(inputs) = action.get("InputArtifacts").and_then(|i| i.as_array()) {
                        for (ia_idx, ia) in inputs.elements.iter().enumerate() {
                            if let Some(ia_name) = ia.get("Name").and_then(|n| n.as_str()) {
                                if !output_names.contains(ia_name) {
                                    issues.push(ValidationError {
                                        rule_id: Some(self.id().to_string()),
                                        message: format!(
                                            "'{}' is not previously defined as an 'OutputArtifact'",
                                            ia_name
                                        ),
                                        path: vec![
                                            "Resources".into(),
                                            name.clone(),
                                            "Properties".into(),
                                            "Stages".into(),
                                            stage_idx.to_string(),
                                            "Actions".into(),
                                            action_idx.to_string(),
                                            "InputArtifacts".into(),
                                            ia_idx.to_string(),
                                            "Name".into(),
                                        ],
                                        span: ia
                                            .get("Name")
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
    fn test_valid_artifact_names() {
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
            - Name: DeployAction
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: S3
                Version: "1"
              InputArtifacts:
                - Name: SourceOutput
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3701.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_undefined_input_artifact() {
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
            - Name: DeployAction
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: S3
                Version: "1"
              InputArtifacts:
                - Name: NonExistent
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3701.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("NonExistent"));
        assert!(issues[0].message.contains("not previously defined"));
    }
}

crate::register_cfn_lint_rule!(E3701);
