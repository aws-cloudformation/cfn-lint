use super::super::{ValidationError, Validator};
use super::helpers::err;
use crate::ast::AstNode;
use regex::Regex;
use std::sync::LazyLock;

static RE_AMI_ID: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^ami-([0-9a-z]{8}|[0-9a-z]{17})$").unwrap());
static RE_SG_ID: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^sg-([a-fA-F0-9]{8}|[a-fA-F0-9]{17})$").unwrap());
static RE_SUBNET_ID: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^subnet-(([0-9A-Fa-f]{8})|([0-9A-Fa-f]{17}))$").unwrap());
static RE_VPC_ID: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^vpc-(([0-9A-Fa-f]{8})|([0-9A-Fa-f]{17}))$").unwrap());
static RE_SG_NAME: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"^[a-zA-Z0-9 \._\-:/()#,@\[\]+=&;\{\}!\$\*]+$"#).unwrap());
static RE_IAM_ROLE_ARN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^arn:(aws|aws-cn|aws-iso|aws-iso-[a-z]{1}|aws-us-gov):iam::\d{12}:role/.*$")
        .unwrap()
});
static RE_LOG_GROUP_NAME: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[\.\-_/#A-Za-z0-9]{1,512}\z").unwrap());
static RE_DATE_TIME: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
    r"^\d{4}-(0[1-9]|1[0-2])-\d{2}T([01]\d|2[0-3]):[0-5]\d:[0-5]\d(\.\d+)?(Z|[+-]([01]\d|2[0-3]):[0-5]\d)$"
).unwrap()
});
static RE_ACM_CERT_ARN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^arn:aws[a-zA-Z-]*:acm:[a-z0-9-]+:\d{12}:certificate/.+$").unwrap()
});
static RE_KMS_KEY_ARN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^arn:aws[a-zA-Z-]*:kms:[a-z0-9-]+:\d{12}:(key|alias)/.+$").unwrap()
});
static RE_SNS_TOPIC_ARN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^arn:aws[a-zA-Z-]*:sns:[a-z0-9-]+:\d{12}:.+$").unwrap());
static RE_LAMBDA_ARN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^arn:aws[a-zA-Z-]*:lambda:[a-z0-9-]+:\d{12}:function:.+(:.+)?$").unwrap()
});
static RE_KMS_KEY_ID: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|mrk-[0-9a-f]{32}|alias/[a-zA-Z0-9/_-]+)$").unwrap()
});
static RE_KMS_ALIAS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^alias/[a-zA-Z0-9:/_-]+$").unwrap());

pub fn validate_format(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let s = match node {
        AstNode::String(s) => s,
        _ => return vec![],
    };
    let format_name = match constraint.as_str() {
        Some(f) => f,
        None => return vec![],
    };

    // Normalize format name: patches use dots (e.g. AWS::EC2::SecurityGroup.Id)
    // but we also accept double-colon form for backward compatibility
    let error_msg = match format_name {
        "AWS::EC2::Image.Id" | "AWS::EC2::Image::Id" => {
            if RE_AMI_ID.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::EC2::Image.Id' with pattern '^ami-([0-9a-z]{{8}}|[0-9a-z]{{17}})$'", s.value))
            }
        }
        "AWS::EC2::SecurityGroup.Id" | "AWS::EC2::SecurityGroup::Id" => {
            if RE_SG_ID.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::EC2::SecurityGroup.Id' with pattern '^sg-([a-fA-F0-9]{{8}}|[a-fA-F0-9]{{17}})$'", s.value))
            }
        }
        "AWS::EC2::Subnet.Id" | "AWS::EC2::Subnet::Id" => {
            if RE_SUBNET_ID.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::EC2::Subnet.Id' with pattern '^subnet-(([0-9A-Fa-f]{{8}})|([0-9A-Fa-f]{{17}}))$'", s.value))
            }
        }
        "AWS::EC2::VPC.Id" | "AWS::EC2::VPC::Id" => {
            if RE_VPC_ID.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::EC2::VPC.Id' with pattern '^vpc-(([0-9A-Fa-f]{{8}})|([0-9A-Fa-f]{{17}}))$'", s.value))
            }
        }
        "AWS::EC2::SecurityGroup.Name" | "AWS::EC2::SecurityGroup::GroupName" => {
            if RE_SG_NAME.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a valid Security Group name", s.value))
            }
        }
        "AWS::IAM::Role.Arn" | "AWS::IAM::Role::Arn" => {
            if RE_IAM_ROLE_ARN.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a valid IAM Role ARN", s.value))
            }
        }
        "AWS::Logs::LogGroup.Name" | "AWS::Logs::LogGroup::Name" => {
            if RE_LOG_GROUP_NAME.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a valid Log Group name", s.value))
            }
        }
        "ipv4-network" => {
            match s.value.parse::<std::net::Ipv4Addr>() {
                Ok(_) => Some(format!("'{}' is not a 'ipv4-network'", s.value)),
                Err(_) => {
                    // Must be CIDR notation: ip/prefix
                    let parts: Vec<&str> = s.value.splitn(2, '/').collect();
                    if parts.len() != 2 {
                        Some(format!("'{}' is not a 'ipv4-network'", s.value))
                    } else {
                        match (
                            parts[0].parse::<std::net::Ipv4Addr>(),
                            parts[1].parse::<u8>(),
                        ) {
                            (Ok(addr), Ok(prefix)) if prefix <= 32 => {
                                // Check no host bits set
                                let ip: u32 = u32::from(addr);
                                let mask = if prefix == 0 {
                                    0u32
                                } else {
                                    !0u32 << (32 - prefix)
                                };
                                if ip & !mask != 0 {
                                    Some(format!("'{}' is not a 'ipv4-network'", s.value))
                                } else {
                                    None
                                }
                            }
                            _ => Some(format!("'{}' is not a 'ipv4-network'", s.value)),
                        }
                    }
                }
            }
        }
        "ipv4" => {
            if s.value.parse::<std::net::Ipv4Addr>().is_err() {
                Some(format!("'{}' is not a 'ipv4'", s.value))
            } else {
                None
            }
        }
        "ipv6" => {
            if s.value.parse::<std::net::Ipv6Addr>().is_err() {
                Some(format!("'{}' is not a 'ipv6'", s.value))
            } else {
                None
            }
        }
        "date-time" => {
            // RFC 3339 date-time: YYYY-MM-DDTHH:MM:SS[.frac](Z|+/-HH:MM)
            if RE_DATE_TIME.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'date-time'", s.value))
            }
        }
        "AWS::KMS::Key.Arn" | "AWS::KMS::Key::Arn" => {
            if RE_KMS_KEY_ARN.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::KMS::Key.Arn'", s.value))
            }
        }
        "AWS::SNS::Topic.Arn" | "AWS::SNS::Topic::Arn" => {
            if RE_SNS_TOPIC_ARN.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::SNS::Topic.Arn'", s.value))
            }
        }
        "AWS::ACM::Certificate.Arn" | "AWS::ACM::Certificate::Arn" => {
            if RE_ACM_CERT_ARN.is_match(&s.value) {
                None
            } else {
                Some(format!(
                    "'{}' is not a 'AWS::ACM::Certificate.Arn'",
                    s.value
                ))
            }
        }
        "AWS::Lambda::Function.Arn" | "AWS::Lambda::Function::Arn" => {
            if RE_LAMBDA_ARN.is_match(&s.value) {
                None
            } else {
                Some(format!(
                    "'{}' is not a 'AWS::Lambda::Function.Arn'",
                    s.value
                ))
            }
        }
        "AWS::KMS::Key.Id" | "AWS::KMS::Key::Id" => {
            if RE_KMS_KEY_ID.is_match(&s.value) {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::KMS::Key.Id'", s.value))
            }
        }
        "AWS::KMS::Alias.AliasName" | "AWS::KMS::Alias::Name" | "AWS::KMS::Key.Alias" => {
            if RE_KMS_ALIAS.is_match(&s.value) {
                None
            } else {
                Some(format!(
                    "'{}' is not a 'AWS::KMS::Alias.AliasName'",
                    s.value
                ))
            }
        }
        "AWS::S3::Bucket.Name" | "AWS::S3::Bucket::Name" => {
            // S3 bucket name: 3-63 chars, lowercase letters, numbers, dots, hyphens
            // Must not start/end with dot or hyphen, no consecutive dots/hyphens
            let val = &s.value;
            let valid = val.len() >= 3
                && val.len() <= 63
                && val.bytes().all(|b| {
                    b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'.' || b == b'-'
                })
                && !val.starts_with('.')
                && !val.starts_with('-')
                && !val.ends_with('.')
                && !val.ends_with('-')
                && !val.contains("..")
                && !val.contains("-.")
                && !val.contains(".-");
            if valid {
                None
            } else {
                Some(format!("'{}' is not a 'AWS::S3::Bucket.Name' with pattern '^(?![.\\-])(?!.*\\.\\.)(?!.*\\-\\.)(?!.*\\.\\-)[a-z0-9.\\-]{{3,63}}(?<![.\\-])$'", s.value))
            }
        }
        _ => None, // Unknown format — skip
    };

    match error_msg {
        Some(msg) => vec![err(&format!("format:{}", format_name), msg, path, node)],
        None => vec![],
    }
}
