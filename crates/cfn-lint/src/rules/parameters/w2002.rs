use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W2002;

impl CfnLintRule for W2002 {
    fn id(&self) -> &str {
        "W2002"
    }
    fn short_description(&self) -> &str {
        "Parameter type is not officially supported by CloudFormation"
    }
    fn description(&self) -> &str {
        "Check if Parameters use unsupported types. CloudFormation accepts any \
         AWS::SSM::Parameter::Value<> or List<> pattern, but only validates specific types."
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Parameters/*/Type"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let type_val = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        // Only flag SSM or List types that aren't in the valid list
        if (type_val.starts_with("AWS::SSM::Parameter::Value<")
            || type_val.starts_with("List<"))
            && !VALID_PARAMETER_TYPES.contains(&type_val)
        {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} is not an officially documented CloudFormation parameter type. \
                     While CloudFormation may accept this type, it will not validate the parameter value.",
                    type_val
                ),
                path: path.to_vec(),
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

const VALID_PARAMETER_TYPES: &[&str] = &[
    // Single types
    "AWS::EC2::AvailabilityZone::Name",
    "AWS::EC2::Image::Id",
    "AWS::EC2::Instance::Id",
    "AWS::EC2::KeyPair::KeyName",
    "AWS::EC2::SecurityGroup::GroupName",
    "AWS::EC2::SecurityGroup::Id",
    "AWS::EC2::Subnet::Id",
    "AWS::EC2::VPC::Id",
    "AWS::EC2::Volume::Id",
    "AWS::Route53::HostedZone::Id",
    "AWS::SSM::Parameter::Name",
    "Number",
    "String",
    "AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Instance::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::KeyPair::KeyName>",
    "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::GroupName>",
    "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Subnet::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Volume::Id>",
    "AWS::SSM::Parameter::Value<AWS::Route53::HostedZone::Id>",
    "AWS::SSM::Parameter::Value<AWS::SSM::Parameter::Name>",
    "AWS::SSM::Parameter::Value<Number>",
    "AWS::SSM::Parameter::Value<String>",
    // List types
    "CommaDelimitedList",
    "List<AWS::EC2::AvailabilityZone::Name>",
    "List<AWS::EC2::Image::Id>",
    "List<AWS::EC2::Instance::Id>",
    "List<AWS::EC2::SecurityGroup::GroupName>",
    "List<AWS::EC2::SecurityGroup::Id>",
    "List<AWS::EC2::Subnet::Id>",
    "List<AWS::EC2::VPC::Id>",
    "List<AWS::EC2::Volume::Id>",
    "List<AWS::Route53::HostedZone::Id>",
    "List<Number>",
    "List<String>",
    "AWS::SSM::Parameter::Value<CommaDelimitedList>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::AvailabilityZone::Name>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Image::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Instance::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::GroupName>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::VPC::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Volume::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::Route53::HostedZone::Id>>",
    "AWS::SSM::Parameter::Value<List<Number>>",
    "AWS::SSM::Parameter::Value<List<String>>",
];

#[cfg(test)]

mod tests {
    use crate::template::Template;
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_types_no_warnings() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
    Default: prod
  Num:
    Type: Number
  CDL:
    Type: CommaDelimitedList
  SSM:
    Type: AWS::SSM::Parameter::Value<String>
  ListStr:
    Type: List<String>
Resources: {}
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2002.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_unsupported_ssm_type_stub() {
        let yaml = br#"
Parameters:
  Param:
    Type: AWS::SSM::Parameter::Value<AWS::Custom::Type>
Resources: {}
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2002.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W2002);
