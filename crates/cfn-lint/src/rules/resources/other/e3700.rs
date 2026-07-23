use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3700: Validate CodePipeline Source actions are only in the first stage.
pub struct E3700;

impl CfnLintRule for E3700 {
    fn id(&self) -> &str {
        "E3700"
    }
    fn short_description(&self) -> &str {
        "Validate CodePipeline Source actions are only in the first stage"
    }
    fn description(&self) -> &str {
        "When using AWS::CodePipeline::Pipeline this rule will validate \
         that Source actions are only used in the first stage"
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
        let resources = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let mut issues = Vec::new();
        for (name, node) in resources.iter() {
            let resource_type = template
                .resources
                .get(name)
                .map(|r| r.resource_type.as_str())
                .unwrap_or("");
            if resource_type != "AWS::CodePipeline::Pipeline" {
                continue;
            }

            let stages = match node
                .get("Properties")
                .and_then(|p| p.get("Stages"))
                .and_then(|s| s.as_array())
            {
                Some(a) => a,
                None => continue,
            };

            for (stage_idx, stage) in stages.elements.iter().enumerate() {
                let actions = match stage.get("Actions").and_then(|a| a.as_array()) {
                    Some(a) => a,
                    None => continue,
                };

                for (action_idx, action) in actions.elements.iter().enumerate() {
                    let category = match action
                        .get("ActionTypeId")
                        .and_then(|a| a.get("Category"))
                        .and_then(|c| c.as_str())
                    {
                        Some(c) => c,
                        None => continue,
                    };

                    if stage_idx == 0 {
                        // First stage: all actions must be Source
                        if category != "Source" {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "The first stage of a pipeline must only contain 'Source' actions, found '{}'",
                                    category
                                ),
                                path: vec![
                                    "Resources".to_string(),
                                    name.to_string(),
                                    "Properties".to_string(),
                                    "Stages".to_string(),
                                    stage_idx.to_string(),
                                    "Actions".to_string(),
                                    action_idx.to_string(),
                                    "ActionTypeId".to_string(),
                                    "Category".to_string(),
                                ],
                                span: action
                                    .get("ActionTypeId")
                                    .and_then(|a| a.get("Category"))
                                    .map(|n| n.span())
                                    .unwrap_or_default(),
                                keyword: String::new(),
                                unknown: false,
                                resolved_from_ref: false,
                                context: vec![],
                                schema_id: None,
});
                        }
                    } else {
                        // Subsequent stages: must NOT be Source
                        if category == "Source" {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: "'Source' actions are only allowed in the first stage of a pipeline".to_string(),
                                path: vec![
                                    "Resources".to_string(),
                                    name.to_string(),
                                    "Properties".to_string(),
                                    "Stages".to_string(),
                                    stage_idx.to_string(),
                                    "Actions".to_string(),
                                    action_idx.to_string(),
                                    "ActionTypeId".to_string(),
                                    "Category".to_string(),
                                ],
                                span: action
                                    .get("ActionTypeId")
                                    .and_then(|a| a.get("Category"))
                                    .map(|n| n.span())
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
    fn test_valid_pipeline() {
        let yaml = br#"
Resources:
  MyPipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      RoleArn: arn:aws:iam::123456789012:role/role
      Stages:
        - Name: Source
          Actions:
            - Name: SourceAction
              ActionTypeId:
                Category: Source
                Owner: AWS
                Provider: S3
                Version: "1"
        - Name: Build
          Actions:
            - Name: BuildAction
              ActionTypeId:
                Category: Build
                Owner: AWS
                Provider: CodeBuild
                Version: "1"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3700.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_source_in_second_stage() {
        let yaml = br#"
Resources:
  MyPipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      RoleArn: arn:aws:iam::123456789012:role/role
      Stages:
        - Name: Source
          Actions:
            - Name: SourceAction
              ActionTypeId:
                Category: Source
                Owner: AWS
                Provider: S3
                Version: "1"
        - Name: BadStage
          Actions:
            - Name: BadAction
              ActionTypeId:
                Category: Source
                Owner: AWS
                Provider: S3
                Version: "1"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3700.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3700"));
        assert!(issues[0].message.contains("Source"));
    }
}

crate::register_cfn_lint_rule!(E3700);
