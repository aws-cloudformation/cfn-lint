use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3503: ValidationDomain must be a superdomain of DomainName.
///
/// In ACM Certificate DomainValidationOptions, the ValidationDomain must
/// either equal or be a superdomain of the DomainName being validated.
pub struct E3503;

impl CfnLintRule for E3503 {
    fn id(&self) -> &str {
        "E3503"
    }

    fn short_description(&self) -> &str {
        "ValidationDomain is superdomain of DomainName"
    }

    fn description(&self) -> &str {
        "In DomainValidationOptions, the ValidationDomain must be a superdomain of the DomainName being validated"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::CertificateManager::Certificate/Properties/DomainValidationOptions/*"]
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

        let domain_name = match obj.get("DomainName").and_then(|n| n.as_str()) {
            Some(s) => s,
            None => return vec![],
        };

        let validation_domain = match obj.get("ValidationDomain").and_then(|n| n.as_str()) {
            Some(s) => s,
            None => return vec![],
        };

        // Equal is valid
        if domain_name == validation_domain {
            return vec![];
        }

        // DomainName must end with ".{ValidationDomain}"
        if !domain_name.ends_with(&format!(".{}", validation_domain)) {
            let mut err_path = path.to_vec();
            err_path.push("DomainName".to_string());

            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} must be a superdomain of {:?}",
                    validation_domain, domain_name
                ),
                path: err_path,
                span: obj
                    .get("DomainName")
                    .map(|n| n.span())
                    .unwrap_or_default(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

crate::register_cfn_lint_rule!(E3503);
