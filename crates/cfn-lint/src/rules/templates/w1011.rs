use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W1011;

impl CfnLintRule for W1011 {
    fn id(&self) -> &str { "W1011" }
    fn short_description(&self) -> &str { "Use dynamic references over parameters for secrets" }
    fn description(&self) -> &str {
        "Instead of REFing a parameter for a secret use a dynamic reference"
    }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::DirectoryService::MicrosoftAD/Properties/Password",
            "Resources/AWS::DirectoryService::SimpleAD/Properties/Password",
            "Resources/AWS::ElastiCache::ReplicationGroup/Properties/AuthToken",
            "Resources/AWS::IAM::User/Properties/LoginProfile/Password",
            "Resources/AWS::KinesisFirehose::DeliveryStream/Properties/RedshiftDestinationConfiguration/Password",
            "Resources/AWS::OpsWorks::App/Properties/AppSource/Password",
            "Resources/AWS::OpsWorks::Stack/Properties/RdsDbInstances/*/DbPassword",
            "Resources/AWS::OpsWorks::Stack/Properties/CustomCookbooksSource/Password",
            "Resources/AWS::RDS::DBCluster/Properties/MasterUserPassword",
            "Resources/AWS::RDS::DBInstance/Properties/MasterUserPassword",
            "Resources/AWS::Redshift::Cluster/Properties/MasterUserPassword",
        ]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        if let AstNode::Function(func) = instance {
            if func.name == "Ref" {
                if let Some(param_name) = func.args.as_str() {
                    let is_parameter = validator.context()
                        .map(|ctx| ctx.template.parameters.contains_key(param_name))
                        .unwrap_or(false);
                    if is_parameter {
                        return vec![ValidationError {
                rule_id: None,
                            message: "Use dynamic references over parameters for secrets"
                                .to_string(),
                            path: path.to_vec(),
                            keyword: String::new(),
                            span: instance.span(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                        schema_id: None,
                        }];
                    }
                }
            }
        }
        vec![]
    }
}

crate::register_cfn_lint_rule!(W1011);
