use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W2530: Validate that SnapStart is properly configured with a Lambda Version resource.
pub struct W2530;

impl CfnLintRule for W2530 {
    fn id(&self) -> &str {
        "W2530"
    }
    fn short_description(&self) -> &str {
        "Validate that SnapStart is properly configured"
    }
    fn description(&self) -> &str {
        "To properly leverage SnapStart, you must configure both the lambda function \
         and attach a Lambda version resource"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(v) => v,
            None => return vec![],
        };

        if val != "PublishedVersions" {
            return vec![];
        }

        // Get the resource name from the path: Resources/<name>/Properties/SnapStart/ApplyOn
        let resource_name = match path.get(1) {
            Some(n) => n,
            None => return vec![],
        };

        // Check if any AWS::Lambda::Version references this function
        let has_version = if let Some(ctx) = validator.context() {
            ctx.template.resources.values().any(|r| {
                if r.resource_type != "AWS::Lambda::Version" {
                    return false;
                }
                if let Some(props) = &r.properties {
                    if let Some(AstNode::Function(f)) = props.get("FunctionName") {
                        if f.name == "Ref" {
                            return f.args.as_str() == Some(resource_name.as_str());
                        }
                    }
                }
                false
            })
        } else {
            // Without context, cannot check cross-resource references
            return vec![];
        };

        if !has_version {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'SnapStart' is enabled but an 'AWS::Lambda::Version' \
                          resource is not attached"
                    .into(),
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
    fn test_snapstart_with_version_ok() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      SnapStart:
        ApplyOn: PublishedVersions
  FuncVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref Func
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_snapstart_without_version_warns() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      SnapStart:
        ApplyOn: PublishedVersions
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("SnapStart"));
    }
}

crate::register_cfn_lint_rule!(W2530);
