use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W2506: Check if ImageId Parameters have the correct type.
pub struct W2506;

impl CfnLintRule for W2506 {
    fn id(&self) -> &str {
        "W2506"
    }
    fn short_description(&self) -> &str {
        "Check if ImageId Parameters have the correct type"
    }
    fn description(&self) -> &str {
        "See if there are any refs for ImageId to a parameter of inappropriate type"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/ImageId",
            "Resources/AWS::Batch::ComputeEnvironment/Properties/ComputeResources/ImageId",
            "Resources/AWS::Cloud9::EnvironmentEC2/Properties/ImageId",
            "Resources/AWS::EC2::Instance/Properties/ImageId",
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/ImageId",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/ImageId",
            "Resources/AWS::ImageBuilder::Image/Properties/ImageId",
        ]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        _path: &[String],
    ) -> Vec<ValidationError> {
        // Extract parameter name from Ref function node
        let param_name = match instance {
            AstNode::Function(func) if func.name == "Ref" => match func.args.as_str() {
                Some(s) => s,
                None => return vec![],
            },
            _ => return vec![],
        };

        // Look up the parameter in the context
        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        let param_info = match ctx.template.parameters.get(param_name) {
            Some(p) => p,
            None => return vec![],
        };

        if !VALID_IMAGE_TYPES.contains(&param_info.param_type.as_str()) {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Parameter {:?} should be of type 'AWS::EC2::Image::Id' or \
                     'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>', got {:?}",
                    param_name, param_info.param_type
                ),
                path: vec![
                    "Parameters".to_string(),
                    param_name.to_string(),
                    "Type".to_string(),
                ],
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

const VALID_IMAGE_TYPES: &[&str] = &[
    "AWS::EC2::Image::Id",
    "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_correct_image_type_ok() {
        let yaml = br#"
Parameters:
  AMI:
    Type: AWS::EC2::Image::Id
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AMI
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2506.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_wrong_image_type_stub() {
        let yaml = br#"
Parameters:
  AMI:
    Type: String
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref AMI
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2506.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W2506);
