use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W4001: Metadata Interface parameters exist.
///
/// Validates that parameters referenced in
/// Metadata/AWS::CloudFormation::Interface actually exist in the template.
pub struct W4001;

impl CfnLintRule for W4001 {
    fn id(&self) -> &str {
        "W4001"
    }
    fn short_description(&self) -> &str {
        "Metadata Interface parameters exist"
    }
    fn description(&self) -> &str {
        "Metadata Interface parameters actually exist"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Metadata/AWS::CloudFormation::Interface"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        let mut errors = Vec::new();

        // Check ParameterGroups
        if let Some(groups) = instance.get("ParameterGroups").and_then(|n| n.as_array()) {
            for group in &groups.elements {
                if let Some(params) = group.get("Parameters").and_then(|n| n.as_array()) {
                    for param in &params.elements {
                        if let Some(name) = param.as_str() {
                            if !ctx.template.parameters.contains_key(name) {
                                let mut p = path.to_vec();
                                p.push("ParameterGroups".to_string());
                                errors.push(ValidationError {
                                    rule_id: None,
                                    keyword: format!("cfnLint:{}", self.id()),
                                    message: format!(
                                        "Parameter {:?} in Metadata Interface does not exist",
                                        name
                                    ),
                                    path: p,
                                    span: param.span(),
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

        // Check ParameterLabels
        if let Some(labels) = instance.get("ParameterLabels").and_then(|n| n.as_object()) {
            for (key, _) in labels.iter() {
                if !ctx.template.parameters.contains_key(key) {
                    let mut p = path.to_vec();
                    p.push("ParameterLabels".to_string());
                    errors.push(ValidationError {
                        rule_id: None,
                        keyword: format!("cfnLint:{}", self.id()),
                        message: format!(
                            "Parameter {:?} in Metadata Interface does not exist",
                            key
                        ),
                        path: p,
                        span: labels.span,
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
        }

        errors
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_valid_interface_params() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Config
        Parameters:
          - Env
    ParameterLabels:
      Env:
        default: Environment
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W4001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_nonexistent_interface_param_stub() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Config
        Parameters:
          - Env
          - Missing
    ParameterLabels:
      Ghost:
        default: Does not exist
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W4001.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W4001);
