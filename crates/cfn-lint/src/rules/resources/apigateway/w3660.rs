use crate::ast::AstNode;
use crate::graph::Graph;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W3660;

impl CfnLintRule for W3660 {
    fn id(&self) -> &str {
        "W3660"
    }
    fn short_description(&self) -> &str {
        "Validate if multiple resources are modifying a Rest API definition"
    }
    fn description(&self) -> &str {
        "When using AWS::ApiGateway::RestApi with Body or BodyS3Location \
         the resource handler uses PutRestApi with mode overwrite which may \
         cause drift and orphaned resources"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::ApiGateway::RestApi/Properties/Body",
            "Resources/AWS::ApiGateway::RestApi/Properties/BodyS3Location",
        ]
    }

    fn validate(
        &self,
        validator: &Validator,
        keyword: &str,
        _instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        // Get resource name from path: ["Resources", "<name>", "Properties", "Body|BodyS3Location"]
        let resource_name = match path.get(1) {
            Some(n) => n.as_str(),
            None => return vec![],
        };

        // Determine which property key triggered this (Body or BodyS3Location)
        let key = keyword.rsplit('/').next().unwrap_or("Body");

        let template = &ctx.template;
        let root = &template.root;
        let graph = Graph::build(template, root);

        // Find child resources that reference this RestApi
        let mut errors = Vec::new();
        let mut seen_sources = std::collections::HashSet::new();

        for edge in &graph.edges {
            if edge.target != resource_name {
                continue;
            }
            let source_type = match template.resources.get(&edge.source) {
                Some(r) => &r.resource_type,
                None => continue,
            };
            if !APIGW_CHILD_TYPES.contains(&source_type.as_str()) {
                continue;
            }
            if !seen_sources.insert(edge.source.clone()) {
                continue;
            }
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Defining {:?} with a relation to resource {:?} of type {:?} \
                     may result in drift and orphaned resources",
                    key, edge.source, source_type
                ),
                path: path.to_vec(),
                span: Default::default(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
        errors
    }
}

const APIGW_CHILD_TYPES: &[&str] = &[
    "AWS::ApiGateway::Method",
    "AWS::ApiGateway::Model",
    "AWS::ApiGateway::Resource",
    "AWS::ApiGateway::GatewayResponse",
    "AWS::ApiGateway::RequestValidator",
    "AWS::ApiGateway::Authorizer",
];

#[cfg(test)]

mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_no_body_no_warning() {
        let yaml = br#"
Resources:
  Api:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: MyApi
  Method:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref Api
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3660.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_body_with_child_stub() {
        let yaml = br#"
Resources:
  Api:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: MyApi
      Body:
        swagger: "2.0"
  Method:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref Api
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3660.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W3660);
