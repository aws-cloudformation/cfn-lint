use std::collections::HashSet;
use std::sync::{LazyLock, Mutex};

use crate::ast::AstNode;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static INTERNED_RULE_IDS: LazyLock<Mutex<HashSet<&'static str>>> =
    LazyLock::new(|| Mutex::new(HashSet::new()));

pub(crate) fn intern_rule_id(s: &str) -> &'static str {
    let mut pool = INTERNED_RULE_IDS.lock().unwrap();
    if let Some(&existing) = pool.get(s) {
        return existing;
    }
    let leaked: &'static str = Box::leak(s.to_string().into_boxed_str());
    pool.insert(leaked);
    leaked
}

pub(crate) fn keyword_to_rule_id(keyword: &str) -> &'static str {
    if let Some(rule_id) = keyword.strip_prefix("cfnLint:") {
        return intern_rule_id(rule_id);
    }
    if keyword.len() <= 5
        && (keyword.starts_with('E') || keyword.starts_with('W') || keyword.starts_with('I'))
        && keyword[1..].chars().all(|c| c.is_ascii_digit())
    {
        return intern_rule_id(keyword);
    }
    if let Some(format_name) = keyword.strip_prefix("format:") {
        return match format_name {
            "AWS::EC2::SecurityGroup.Id" | "AWS::EC2::SecurityGroup::Id" => "E1150",
            "AWS::EC2::VPC.Id" | "AWS::EC2::VPC::Id" => "E1151",
            "AWS::EC2::Image.Id" | "AWS::EC2::Image::Id" => "E1152",
            "AWS::EC2::SecurityGroup.Name" | "AWS::EC2::SecurityGroup::GroupName" => "E1153",
            "AWS::EC2::Subnet.Id" | "AWS::EC2::Subnet::Id" => "E1154",
            "AWS::Logs::LogGroup.Name" | "AWS::Logs::LogGroup::Name" => "E1155",
            "AWS::IAM::Role.Arn" | "AWS::IAM::Role::Arn" => "E1156",
            "AWS::KMS::Key.Arn" | "AWS::KMS::Key::Arn" => "E1157",
            "AWS::SNS::Topic.Arn" | "AWS::SNS::Topic::Arn" => "E1158",
            "AWS::ACM::Certificate.Arn" | "AWS::ACM::Certificate::Arn" => "E1159",
            "AWS::Lambda::Function.Arn" | "AWS::Lambda::Function::Arn" => "E1160",
            "AWS::S3::Bucket.Name" | "AWS::S3::Bucket::Name" => "E1161",
            "AWS::KMS::Key.Id" | "AWS::KMS::Key::Id" => "E1162",
            "AWS::KMS::Alias.Name" | "AWS::KMS::Alias::Name" | "AWS::KMS::Key.Alias" => "E1164",
            "date-time" => "E3002",
            _ => "E3031",
        };
    }
    match keyword {
        "format" => "E3031",
        "pattern" => "E3031",
        "required" => "E3003",
        "dependentRequired" => "E3021",
        "dependentExcluded" => "E3020",
        "enum" | "const" | "enumCaseInsensitive" => "E3030",
        "minimum" | "maximum" | "exclusiveMinimum" | "exclusiveMaximum" | "multipleOf" => "E3034",
        "uniqueItems" | "uniqueKeys" => "E3037",
        "prefixItems" => "E3008",
        "requiredXor" => "E3014",
        "requiredOr" => "E3058",
        "propertyNames" => "E3011",
        "additionalProperties" => "E3002",
        "maxProperties" => "E3010",
        "type" => "E3012",
        "minItems" | "maxItems" => "E3032",
        "maxUniqueItems" => "E3065",
        "minLength" | "maxLength" => "E3033",
        "anyOf" => "E3017",
        "oneOf" => "E3018",
        "fn_if" => "E1028",
        "fn_getatt" => "E1010",
        "fn_base64" => "E1021",
        "fn_findinmap" => "E1011",
        "fn_sub" => "E1019",
        "fn_join" => "E1022",
        "fn_select" => "E1017",
        "fn_split" => "E1018",
        "fn_getazs" => "E1015",
        "fn_importvalue" => "E1016",
        "fn_cidr" => "E1029",
        "fn_getstackoutput" => "E1033",
        "fn_equals" => "E8003",
        "fn_condition" => "E8004",
        _ => "E3001",
    }
}

pub(crate) const TEMPLATED_PROPERTY_PATHS: &[&str] = &[
    "Resources/AWS::ApiGateway::RestApi/Properties/BodyS3Location",
    "Resources/AWS::AppSync::FunctionConfiguration/Properties/RequestMappingTemplateS3Location",
    "Resources/AWS::AppSync::FunctionConfiguration/Properties/ResponseMappingTemplateS3Location",
    "Resources/AWS::AppSync::GraphQLSchema/Properties/DefinitionS3Location",
    "Resources/AWS::AppSync::Resolver/Properties/RequestMappingTemplateS3Location",
    "Resources/AWS::AppSync::Resolver/Properties/ResponseMappingTemplateS3Location",
    "Resources/AWS::CloudFormation::Stack/Properties/TemplateURL",
    "Resources/AWS::CodeCommit::Repository/Properties/Code/S3",
    "Resources/AWS::ElasticBeanstalk::ApplicationVersion/Properties/SourceBundle",
    "Resources/AWS::Lambda::Function/Properties/Code",
    "Resources/AWS::Lambda::LayerVersion/Properties/Content",
    "Resources/AWS::StepFunctions::StateMachine/Properties/DefinitionS3Location",
];

pub(crate) fn is_templated_property(err_path: &[String], resource_type: &str) -> bool {
    if err_path.len() < 3 {
        return false;
    }
    let prop_path = err_path[2..].join("/");
    let check = format!("Resources/{}/{}", resource_type, prop_path);
    TEMPLATED_PROPERTY_PATHS
        .iter()
        .any(|p| check.starts_with(p))
}

pub(crate) fn check_equals_comma_delimited(
    node: &AstNode,
    template: &Template,
    issues: &mut Vec<ValidationError>,
) {
    match node {
        AstNode::Function(func) if func.name == "Fn::Equals" => {
            if let Some(arr) = func.args.as_array() {
                for elem in &arr.elements {
                    if let Some(ref_func) = elem.as_function() {
                        if ref_func.name == "Ref" {
                            if let Some(ref_name) = ref_func.args.as_str() {
                                if let Some(param) = template.parameters.get(ref_name) {
                                    if param.param_type == "CommaDelimitedList" {
                                        issues.push(ValidationError {
                                            rule_id: Some("E1020".to_string()),
                                            message: format!(
                                                "{{'Ref': '{}'}} is not of type 'string'",
                                                ref_name
                                            ),
                                            path: vec![],
                                            span: elem.span().clone(),
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
        }
        AstNode::Function(func) => check_equals_comma_delimited(&func.args, template, issues),
        AstNode::Array(arr) => {
            for elem in &arr.elements {
                check_equals_comma_delimited(elem, template, issues);
            }
        }
        AstNode::Object(obj) => {
            for val in obj.values() {
                check_equals_comma_delimited(val, template, issues);
            }
        }
        _ => {}
    }
}
