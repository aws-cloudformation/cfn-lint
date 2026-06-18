use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W3703: VPNGateway Type should be ipsec.1
pub struct W3703;

impl CfnLintRule for W3703 {
    fn id(&self) -> &str {
        "W3703"
    }
    fn short_description(&self) -> &str {
        "VPNGateway Type should be ipsec.1"
    }
    fn description(&self) -> &str {
        "The only supported value for AWS::EC2::VPNGateway Type is 'ipsec.1'. \
         Other values may not be available."
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::EC2::VPNGateway/Properties/Type"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(v) => v,
            None => return vec![],
        };

        if val != "ipsec.1" {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} is not 'ipsec.1'. Only 'ipsec.1' is supported for VPNGateway Type.",
                    val
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::AstNode;
    use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
    use crate::parser;
    use crate::rules::Issue;
    use crate::template::Template;

    #[test]
    fn test_invalid_type_flagged() {
        let yaml = br#"
Resources:
  VGW:
    Type: AWS::EC2::VPNGateway
    Properties:
      Type: other
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        // Simulate keyword dispatch: get the node at the keyword path
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("VGW")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("Type")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "VGW".to_string(),
            "Properties".to_string(),
            "Type".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3703.validate(
            &validator,
            "Resources/AWS::EC2::VPNGateway/Properties/Type",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
    }

    #[test]
    fn test_ipsec1_ok() {
        let yaml = br#"
Resources:
  VGW:
    Type: AWS::EC2::VPNGateway
    Properties:
      Type: ipsec.1
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("VGW")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("Type")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "VGW".to_string(),
            "Properties".to_string(),
            "Type".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3703.validate(
            &validator,
            "Resources/AWS::EC2::VPNGateway/Properties/Type",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(W3703);
