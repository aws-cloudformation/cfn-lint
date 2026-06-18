use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E2002;

const VALID_TYPES: &[&str] = &[
    "String",
    "Number",
    "CommaDelimitedList",
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
];

fn is_valid_type(t: &str) -> bool {
    VALID_TYPES.contains(&t)
        || t.starts_with("AWS::SSM::Parameter::Value<")
        || t.starts_with("List<")
}

impl CfnLintRule for E2002 {
    fn id(&self) -> &str {
        "E2002"
    }

    fn short_description(&self) -> &str {
        "Parameters have appropriate type"
    }

    fn description(&self) -> &str {
        "Making sure the parameters have a correct type"
    }

    fn severity(&self) -> Severity {
        Severity::Error
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

        if is_valid_type(type_val) {
            return vec![];
        }

        vec![ValidationError {
            rule_id: None,
            keyword: format!("cfnLint:{}", self.id()),
            message: format!("{:?} is not a valid parameter type", type_val),
            path: path.to_vec(),
            span: instance.span(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        }]
    }
}

crate::register_cfn_lint_rule!(E2002);
