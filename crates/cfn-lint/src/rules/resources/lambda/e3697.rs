use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3697: Validate Lambda environment variables do not exceed 4 KB.
pub struct E3697;

impl CfnLintRule for E3697 {
    fn id(&self) -> &str {
        "E3697"
    }
    fn short_description(&self) -> &str {
        "Validate Lambda environment variables do not exceed 4 KB"
    }
    fn description(&self) -> &str {
        "AWS Lambda limits the total size of all environment variables \
         to 4 KB. This rule sums the lengths of all keys and values and \
         validates the total does not exceed 4096 bytes."
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties/Environment/Variables"]
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

        let total: usize = obj
            .iter()
            .map(|(k, v)| {
                let vlen = v.as_str().map(|s| s.len()).unwrap_or(0);
                k.len() + vlen
            })
            .sum();

        const MAX_SIZE: usize = 4096;
        if total > MAX_SIZE {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Lambda environment variables total size ({}) exceeds the 4 KB ({} bytes) limit",
                    total, MAX_SIZE
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
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_stubbed_out() {
        let yaml = br#"
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      Environment:
        Variables:
          KEY1: value1
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3697.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3697);
