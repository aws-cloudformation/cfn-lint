use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W3045: Controlling access to an S3 bucket should be done with bucket policies.
///
/// Warns when `AccessControl` is set on an S3 bucket, since it is a legacy
/// property and bucket policies should be used instead.
pub struct W3045;

impl CfnLintRule for W3045 {
    fn id(&self) -> &str { "W3045" }
    fn short_description(&self) -> &str {
        "Controlling access to an S3 bucket should be done with bucket policies"
    }
    fn description(&self) -> &str {
        "Nearly all access control configurations can be more successfully achieved \
         with bucket policies. Consider using bucket policies instead of access control."
    }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::S3::Bucket/Properties"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        if let Some(ac) = instance.get("AccessControl") {
            let mut ac_path = path.to_vec();
            ac_path.push("AccessControl".to_string());
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'AccessControl' is a legacy property. Consider using \
                          'AWS::S3::BucketPolicy' instead"
                    .to_string(),
                path: ac_path,
                span: ac.span(),
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
    use crate::template::Template;
    use super::*;
    use crate::parser;

    #[test]
    fn test_bucket_without_access_control() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3045.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_bucket_with_access_control_stub() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      AccessControl: PublicRead
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3045.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_non_s3_resource_ignored() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.12
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3045.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_bucket_no_properties() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3045.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W3045);
