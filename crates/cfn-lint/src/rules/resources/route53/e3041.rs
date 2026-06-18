use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3041: RecordSet HostedZoneName is superdomain of Name.
pub struct E3041;

impl CfnLintRule for E3041 {
    fn id(&self) -> &str {
        "E3041"
    }
    fn short_description(&self) -> &str {
        "RecordSet HostedZoneName is superdomain of Name"
    }
    fn description(&self) -> &str {
        "Validates Route53 RecordSet Name matches HostedZoneName"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Route53::RecordSet/Properties"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let obj = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let hosted_zone_name = match obj.get("HostedZoneName").and_then(|n| n.as_str()) {
            Some(s) => s,
            None => return vec![],
        };

        let record_name = match obj.get("Name").and_then(|n| n.as_str()) {
            Some(s) => s,
            None => return vec![],
        };

        let mut errors = Vec::new();

        // HostedZoneName must end with "."
        let hz_normalized = if !hosted_zone_name.ends_with('.') {
            let mut hz_path = path.to_vec();
            hz_path.push("HostedZoneName".to_string());
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!("{:?} must end in a dot", hosted_zone_name),
                path: hz_path,
                span: obj
                    .get("HostedZoneName")
                    .map(|n| n.span())
                    .unwrap_or_default(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
            format!("{}.", hosted_zone_name)
        } else {
            hosted_zone_name.to_string()
        };

        // Normalize Name: add trailing dot if missing
        let name_normalized = if record_name.ends_with('.') {
            record_name.to_string()
        } else {
            format!("{}.", record_name)
        };

        // Name must equal HostedZoneName or end with ".{HostedZoneName}"
        if name_normalized != hz_normalized
            && !name_normalized.ends_with(&format!(".{}", hz_normalized))
        {
            let mut name_path = path.to_vec();
            name_path.push("Name".to_string());
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} must be a subdomain of or equal to {:?}",
                    record_name, hosted_zone_name
                ),
                path: name_path,
                span: obj.get("Name").map(|n| n.span()).unwrap_or_default(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        errors
    }
}

crate::register_cfn_lint_rule!(E3041);
