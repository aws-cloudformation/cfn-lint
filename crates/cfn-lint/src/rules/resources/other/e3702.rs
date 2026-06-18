use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3702: Validate the number of input and output artifacts in a CodePipeline.
pub struct E3702;

impl CfnLintRule for E3702 {
    fn id(&self) -> &str {
        "E3702"
    }
    fn short_description(&self) -> &str {
        "Validate CodePipeline artifact counts"
    }
    fn description(&self) -> &str {
        "Action types have different constraints for InputArtifacts and OutputArtifacts counts"
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

            for (si, stage) in stages.elements.iter().enumerate() {
                let actions = match stage.get("Actions").and_then(|a| a.as_array()) {
                    Some(a) => a,
                    None => continue,
                };
                for (ai, action) in actions.elements.iter().enumerate() {
                    let action_type = match action.get("ActionTypeId") {
                        Some(at) => at,
                        None => continue,
                    };
                    let owner = action_type
                        .get("Owner")
                        .and_then(|n| n.as_str())
                        .unwrap_or("");
                    let category = action_type
                        .get("Category")
                        .and_then(|n| n.as_str())
                        .unwrap_or("");
                    let provider = action_type
                        .get("Provider")
                        .and_then(|n| n.as_str())
                        .unwrap_or("");

                    let constraint = match get_constraint(owner, category, provider) {
                        Some(c) => c,
                        None => continue,
                    };

                    let input_count = action
                        .get("InputArtifacts")
                        .and_then(|n| n.as_array())
                        .map(|a| a.elements.len())
                        .unwrap_or(0);
                    let output_count = action
                        .get("OutputArtifacts")
                        .and_then(|n| n.as_array())
                        .map(|a| a.elements.len())
                        .unwrap_or(0);

                    let repr = format!(
                        "{{'Owner': '{}', 'Category': '{}', 'Provider': '{}'}}",
                        owner, category, provider
                    );
                    let base_path = vec![
                        "Resources".into(),
                        name.clone(),
                        "Properties".into(),
                        "Stages".into(),
                        si.to_string(),
                        "Actions".into(),
                        ai.to_string(),
                    ];

                    if input_count < constraint.min_input {
                        let mut path = base_path.clone();
                        path.push("InputArtifacts".into());
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "InputArtifacts has {} items but minimum is {} when using {}",
                                input_count, constraint.min_input, repr
                            ),
                            path,
                            span: action.span().clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                    if input_count > constraint.max_input {
                        let mut path = base_path.clone();
                        path.push("InputArtifacts".into());
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "InputArtifacts has {} items but maximum is {} when using {}",
                                input_count, constraint.max_input, repr
                            ),
                            path,
                            span: action.span().clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                    if output_count < constraint.min_output {
                        let mut path = base_path.clone();
                        path.push("OutputArtifacts".into());
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "OutputArtifacts has {} items but minimum is {} when using {}",
                                output_count, constraint.min_output, repr
                            ),
                            path,
                            span: action.span().clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                    if output_count > constraint.max_output {
                        let mut path = base_path.clone();
                        path.push("OutputArtifacts".into());
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "OutputArtifacts has {} items but maximum is {} when using {}",
                                output_count, constraint.max_output, repr
                            ),
                            path,
                            span: action.span().clone(),
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
        issues
    }
}

struct ArtifactConstraint {
    min_input: usize,
    max_input: usize,
    min_output: usize,
    max_output: usize,
}

fn get_constraint(owner: &str, category: &str, provider: &str) -> Option<ArtifactConstraint> {
    match (owner, category, provider) {
        ("AWS", "Source", "S3" | "CodeCommit" | "ECR") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 0,
            min_output: 1,
            max_output: 1,
        }),
        ("AWS", "Test", "CodeBuild") => Some(ArtifactConstraint {
            min_input: 1,
            max_input: 5,
            min_output: 0,
            max_output: 5,
        }),
        ("AWS", "Test", "DeviceFarm") => Some(ArtifactConstraint {
            min_input: 1,
            max_input: 1,
            min_output: 0,
            max_output: 0,
        }),
        ("AWS", "Build", "CodeBuild") => Some(ArtifactConstraint {
            min_input: 1,
            max_input: 5,
            min_output: 0,
            max_output: 5,
        }),
        ("AWS", "Approval", "Manual") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 0,
            min_output: 0,
            max_output: 0,
        }),
        ("AWS", "Deploy", "S3") => Some(ArtifactConstraint {
            min_input: 1,
            max_input: 1,
            min_output: 0,
            max_output: 0,
        }),
        ("AWS", "Deploy", "CloudFormation") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 10,
            min_output: 0,
            max_output: 1,
        }),
        (
            "AWS",
            "Deploy",
            "CodeDeploy" | "ElasticBeanstalk" | "OpsWorks" | "ECS" | "ServiceCatalog",
        ) => Some(ArtifactConstraint {
            min_input: 1,
            max_input: 1,
            min_output: 0,
            max_output: 0,
        }),
        ("AWS", "Invoke", "Lambda") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 5,
            min_output: 0,
            max_output: 5,
        }),
        ("ThirdParty", "Source", "GitHub") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 0,
            min_output: 1,
            max_output: 1,
        }),
        ("ThirdParty", "Deploy", "AlexaSkillsKit") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 2,
            min_output: 0,
            max_output: 0,
        }),
        ("Custom", "Build" | "Test", "Jenkins") => Some(ArtifactConstraint {
            min_input: 0,
            max_input: 5,
            min_output: 0,
            max_output: 5,
        }),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_artifact_counts() {
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
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3702.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_too_many_input_artifacts() {
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
              InputArtifacts:
                - Name: Bad
              OutputArtifacts:
                - Name: SourceOutput
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3702.validate_template(&tmpl, &ast);
        assert!(!issues.is_empty());
        assert!(issues
            .iter()
            .any(|i| i.message.contains("InputArtifacts") && i.message.contains("maximum is 0")));
    }
}

crate::register_cfn_lint_rule!(E3702);
