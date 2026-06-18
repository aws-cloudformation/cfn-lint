use std::collections::HashMap;
use thiserror::Error;

use crate::ast::*;

#[derive(Error, Debug)]
pub enum TemplateError {
    #[error("Root node is not an object")]
    RootNotObject,
}

/// Immutable CloudFormation template with structured registries for lookup.
#[derive(Debug, Clone)]
pub struct Template {
    pub root: AstNode,
    pub parameters: HashMap<String, Parameter>,
    pub resources: HashMap<String, Resource>,
    pub conditions: HashMap<String, AstNode>,
    pub mappings: HashMap<String, AstNode>,
    pub outputs: HashMap<String, AstNode>,
    pub description: Option<String>,
    pub version: Option<String>,
    pub filename: Option<String>,
}

#[derive(Debug, Clone)]
pub struct Parameter {
    pub param_type: String,
    pub default: Option<AstNode>,
    pub allowed_values: Option<Vec<AstNode>>,
    pub description: Option<String>,
    pub no_echo: bool,
}

#[derive(Debug, Clone)]
pub struct Resource {
    pub resource_type: String,
    pub properties: Option<AstNode>,
    pub condition: Option<String>,
    pub depends_on: Vec<String>,
    pub metadata: Option<AstNode>,
    /// Valid GetAtt attribute names, populated by the engine.
    pub valid_atts: Vec<String>,
}

impl Template {
    /// Build a Template from a parsed AST root node.
    pub fn from_ast(root: &AstNode) -> Result<Template, TemplateError> {
        let obj = root.as_object().ok_or(TemplateError::RootNotObject)?;

        Ok(Template {
            parameters: parse_parameters(obj),
            resources: parse_resources(obj),
            conditions: parse_section(obj, "Conditions"),
            mappings: parse_section(obj, "Mappings"),
            outputs: parse_section(obj, "Outputs"),
            description: obj
                .get("Description")
                .and_then(|n| n.as_str())
                .map(String::from),
            version: obj
                .get("AWSTemplateFormatVersion")
                .and_then(|n| n.as_str())
                .map(String::from),
            root: root.clone(),
            filename: None,
        })
    }

    pub fn get_parameter(&self, name: &str) -> Option<&Parameter> {
        self.parameters.get(name)
    }

    pub fn get_resource(&self, name: &str) -> Option<&Resource> {
        self.resources.get(name)
    }

    pub fn get_condition(&self, name: &str) -> Option<&AstNode> {
        self.conditions.get(name)
    }
}

/// Extract an object section as a HashMap of name → AstNode (cloned).
fn parse_section(root: &ObjectNode, key: &str) -> HashMap<String, AstNode> {
    match root.get(key).and_then(|n| n.as_object()) {
        Some(obj) => obj
            .iter()
            .map(|(k, v)| (k.to_string(), v.clone()))
            .collect(),
        None => HashMap::new(),
    }
}

fn parse_parameters(root: &ObjectNode) -> HashMap<String, Parameter> {
    let mut map = HashMap::new();
    let section = match root.get("Parameters").and_then(|n| n.as_object()) {
        Some(obj) => obj,
        None => return map,
    };

    for (name, node) in section.iter() {
        if let Some(param) = parse_one_parameter(node) {
            map.insert(name.to_string(), param);
        }
    }
    map
}

fn parse_one_parameter(node: &AstNode) -> Option<Parameter> {
    let obj = node.as_object()?;
    let param_type = obj.get("Type")?.as_str()?.to_string();

    let default = obj.get("Default").cloned();

    let allowed_values = obj
        .get("AllowedValues")
        .and_then(|n| n.as_array())
        .map(|a| a.elements.clone());

    let description = obj
        .get("Description")
        .and_then(|n| n.as_str())
        .map(String::from);

    let no_echo = obj.get("NoEcho").and_then(|n| n.as_bool()).unwrap_or(false);

    Some(Parameter {
        param_type,
        default,
        allowed_values,
        description,
        no_echo,
    })
}

fn parse_resources(root: &ObjectNode) -> HashMap<String, Resource> {
    let mut map = HashMap::new();
    let section = match root.get("Resources").and_then(|n| n.as_object()) {
        Some(obj) => obj,
        None => return map,
    };

    for (name, node) in section.iter() {
        if let Some(res) = parse_one_resource(node) {
            map.insert(name.to_string(), res);
        }
    }
    map
}

fn parse_one_resource(node: &AstNode) -> Option<Resource> {
    let obj = node.as_object()?;
    let resource_type = obj.get("Type")?.as_str()?.to_string();

    let properties = obj.get("Properties").cloned();
    let condition = obj
        .get("Condition")
        .and_then(|n| n.as_str())
        .map(String::from);
    let metadata = obj.get("Metadata").cloned();

    let depends_on = match obj.get("DependsOn") {
        Some(AstNode::String(s)) => vec![s.value.clone()],
        Some(AstNode::Array(a)) => a
            .elements
            .iter()
            .filter_map(|e| e.as_str().map(String::from))
            .collect(),
        _ => vec![],
    };

    Some(Resource {
        resource_type,
        properties,
        condition,
        depends_on,
        metadata,
        valid_atts: vec![],
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_full_template() {
        let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: My test template
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Deployment environment
  EnableFeature:
    Type: String
    NoEcho: true
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Environment
      - prod
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345678
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Condition: IsProd
    DependsOn: OtherResource
    Properties:
      BucketName: my-bucket
    Metadata:
      Comment: A bucket
  OtherResource:
    Type: AWS::SNS::Topic
Outputs:
  BucketArn:
    Value: !GetAtt MyBucket.Arn
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        // Version and description
        assert_eq!(tmpl.version.as_deref(), Some("2010-09-09"));
        assert_eq!(tmpl.description.as_deref(), Some("My test template"));

        // Parameters
        assert_eq!(tmpl.parameters.len(), 2);
        let env = tmpl.get_parameter("Environment").unwrap();
        assert_eq!(env.param_type, "String");
        assert_eq!(env.default.as_ref().unwrap().as_str(), Some("dev"));
        assert_eq!(env.allowed_values.as_ref().unwrap().len(), 3);
        assert_eq!(env.description.as_deref(), Some("Deployment environment"));
        assert!(!env.no_echo);

        let feature = tmpl.get_parameter("EnableFeature").unwrap();
        assert!(feature.no_echo);
        assert!(feature.default.is_none());
        assert!(feature.allowed_values.is_none());

        // Resources
        assert_eq!(tmpl.resources.len(), 2);
        let bucket = tmpl.get_resource("MyBucket").unwrap();
        assert_eq!(bucket.resource_type, "AWS::S3::Bucket");
        assert_eq!(bucket.condition.as_deref(), Some("IsProd"));
        assert_eq!(bucket.depends_on, vec!["OtherResource"]);
        assert!(bucket.properties.is_some());
        assert!(bucket.metadata.is_some());

        let topic = tmpl.get_resource("OtherResource").unwrap();
        assert_eq!(topic.resource_type, "AWS::SNS::Topic");
        assert!(topic.condition.is_none());
        assert!(topic.depends_on.is_empty());
        assert!(topic.properties.is_none());

        // Conditions
        assert_eq!(tmpl.conditions.len(), 1);
        let cond = tmpl.get_condition("IsProd").unwrap();
        // Fn::Equals is not a CFN intrinsic function in the parser,
        // Condition functions are parsed as Function nodes
        assert!(cond.as_function().is_some() || cond.as_object().is_some());

        // Mappings
        assert_eq!(tmpl.mappings.len(), 1);
        assert!(tmpl.mappings.contains_key("RegionMap"));

        // Outputs
        assert_eq!(tmpl.outputs.len(), 1);
        assert!(tmpl.outputs.contains_key("BucketArn"));
    }

    #[test]
    fn test_root_not_object() {
        let ast = AstNode::String(StringNode {
            value: "not an object".into(),
            span: Span::default(),
        });
        let err = Template::from_ast(&ast).unwrap_err();
        assert!(err.to_string().contains("not an object"));
    }

    #[test]
    fn test_empty_template() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        assert_eq!(tmpl.version.as_deref(), Some("2010-09-09"));
        assert!(tmpl.description.is_none());
        assert!(tmpl.parameters.is_empty());
        assert!(tmpl.resources.is_empty());
        assert!(tmpl.conditions.is_empty());
        assert!(tmpl.mappings.is_empty());
        assert!(tmpl.outputs.is_empty());
    }

    #[test]
    fn test_depends_on_array() {
        let yaml = br#"
Resources:
  MyResource:
    Type: AWS::SNS::Topic
    DependsOn:
      - ResourceA
      - ResourceB
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let res = tmpl.get_resource("MyResource").unwrap();
        assert_eq!(res.depends_on, vec!["ResourceA", "ResourceB"]);
    }

    #[test]
    fn test_parameter_without_type_skipped() {
        let yaml = br#"
Parameters:
  BadParam:
    Default: foo
  GoodParam:
    Type: String
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert_eq!(tmpl.parameters.len(), 1);
        assert!(tmpl.get_parameter("GoodParam").is_some());
        assert!(tmpl.get_parameter("BadParam").is_none());
    }

    #[test]
    fn test_resource_without_type_skipped() {
        let yaml = br#"
Resources:
  BadResource:
    Properties:
      Name: test
  GoodResource:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert_eq!(tmpl.resources.len(), 1);
        assert!(tmpl.get_resource("GoodResource").is_some());
        assert!(tmpl.get_resource("BadResource").is_none());
    }
}
