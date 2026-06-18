use crate::ast::AstNode;
use crate::graph::{self, EdgeKind, Graph};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct W1001;

impl CfnLintRule for W1001 {
    fn id(&self) -> &str {
        "W1001"
    }
    fn short_description(&self) -> &str {
        "Ref/GetAtt to resource that is available when conditions are applied"
    }
    fn description(&self) -> &str {
        "Check that Ref/GetAtt targets are available given the conditions along the path"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let dep_graph = Graph::build(template, root);
        let mut issues = Vec::new();

        for edge in &dep_graph.edges {
            // DependsOn is handled by E3005
            if edge.kind == EdgeKind::DependsOn {
                continue;
            }
            // Target must be a resource
            if !template.resources.contains_key(&edge.target) {
                continue;
            }
            // Skip edges from Metadata (e.g. cfn-init) — runtime refs, not deploy-time
            if edge.source_path.first().map(|s| s.as_str()) == Some("Metadata") {
                continue;
            }

            // Build the full path: Resources/<source>/<source_path...>
            let source_name = edge.source.replace("Output-", "");
            let section = if edge.source.starts_with("Output-") {
                "Outputs"
            } else {
                "Resources"
            };
            let mut path = vec![section.to_string(), source_name];
            path.extend(edge.source_path.clone());

            for scenario in graph::is_resource_available(template, root, &path, &edge.target) {
                let scenario_text = scenario
                    .iter()
                    .map(|(k, v)| format!("when condition '{}' is {}", k, v))
                    .collect::<Vec<_>>()
                    .join(" and ");
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "{} to resource '{}' that may not be available {} at {}",
                        edge.kind.label(),
                        edge.target,
                        scenario_text,
                        path.join("/"),
                    ),
                    path: path.clone(),
                    span: Default::default(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
});
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
    fn test_no_warning_unconditional() {
        let yaml = br#"
Resources:
  Topic:
    Type: AWS::SNS::Topic
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_warning_conditional_ref() {
        let yaml = br#"
Conditions:
  CreateIt:
    Fn::Equals: [a, b]
Resources:
  Topic:
    Type: AWS::SNS::Topic
    Condition: CreateIt
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W1001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("may not be available"));
    }

    #[test]
    fn test_no_warning_same_condition() {
        let yaml = br#"
Conditions:
  CreateIt:
    Fn::Equals: [a, b]
Resources:
  Topic:
    Type: AWS::SNS::Topic
    Condition: CreateIt
  Bucket:
    Type: AWS::S3::Bucket
    Condition: CreateIt
    Properties:
      BucketName: !Ref Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1001.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W1001);
