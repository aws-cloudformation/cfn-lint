use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3038: Check if Serverless Resources exist without the Serverless Transform.
pub struct E3038;

impl CfnLintRule for E3038 {
    fn id(&self) -> &str {
        "E3038"
    }
    fn short_description(&self) -> &str {
        "Check if Serverless Resources have Serverless Transform"
    }
    fn description(&self) -> &str {
        "Check that a template with Serverless Resources also includes the Serverless Transform"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/Type"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let type_val = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        if !type_val.starts_with("AWS::Serverless::") {
            return vec![];
        }

        // Check if the template has the serverless transform
        let has_sam = validator
            .context()
            .map(|ctx| {
                // Check the template root for Transform
                let root = &ctx.template.root;
                crate::transform::is_sam_template(root)
            })
            .unwrap_or(false);

        if has_sam {
            return vec![];
        }

        vec![ValidationError {
            rule_id: None,
            keyword: format!("cfnLint:{}", self.id()),
            message: format!(
                "{:?} type used without the serverless transform 'AWS::Serverless-2016-10-31'",
                type_val
            ),
            path: path.to_vec(),
            span: instance.span(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        }]
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
  MyFunc:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3038.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3038);
