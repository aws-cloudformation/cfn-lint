/// E3051 — Validate the structure of an SSM document.
///
/// Loads `data/schemas/other/ssm/document.json` and validates the Content
/// property of AWS::SSM::Document resources. For string Content, parses
/// as JSON first.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3051;

impl CfnLintRule for E3051 {
    fn id(&self) -> &str {
        "E3051"
    }
    fn short_description(&self) -> &str {
        "Validate the structure of a SSM document"
    }
    fn description(&self) -> &str {
        "SSM documents are nested JSON/YAML in CloudFormation. This rule validates those documents."
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let resources = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let schema_path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("data/schemas/other/ssm/document.json");
        let schema: serde_json::Value = match std::fs::read_to_string(&schema_path)
            .ok()
            .and_then(|c| serde_json::from_str(&c).ok())
        {
            Some(s) => s,
            None => return vec![],
        };

        let validator = Validator::new(schema.clone());
        let mut issues = Vec::new();

        for (name, node) in resources.iter() {
            match template.resources.get(name) {
                Some(r) if r.resource_type == "AWS::SSM::Document" => {}
                _ => continue,
            }

            let content = match node.get("Properties").and_then(|p| p.get("Content")) {
                Some(c) => c,
                None => continue,
            };

            if content.as_function().is_some() {
                continue;
            }

            let base_path: Vec<String> = vec![
                "Resources".into(),
                name.to_string(),
                "Properties".into(),
                "Content".into(),
            ];

            if let Some(s) = content.as_str() {
                // Try JSON first, then YAML
                let parsed: Option<AstNode> = crate::parser::parse_json(s.as_bytes())
                    .ok()
                    .or_else(|| crate::parser::parse(s.as_bytes()).ok());

                let is_yaml = crate::parser::parse_json(s.as_bytes()).is_err();

                if let Some(ast_node) = parsed {
                    // Use strict types for YAML content (YAML has type ambiguity)
                    let v = if is_yaml {
                        Validator::new_strict(schema.clone())
                    } else {
                        Validator::new(schema.clone())
                    };
                    let errors = v.validate(&ast_node, &schema, &base_path);
                    issues.extend(errors.into_iter().map(|err| ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: err.message,
                        path: err.path,
                        span: content.span().clone(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    }));
                }
            } else if content.as_object().is_some() {
                let errors = validator.validate(content, &schema, &base_path);
                issues.extend(errors.into_iter().map(|err| ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: err.message,
                    path: err.path,
                    span: content.span().clone(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }));
            }
        }

        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_ssm_document() {
        let yaml = br#"
Resources:
  MyDoc:
    Type: AWS::SSM::Document
    Properties:
      Content: '{"schemaVersion":"2.2","description":"test"}'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3051.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_missing_schema_version() {
        let yaml = br#"
Resources:
  MyDoc:
    Type: AWS::SSM::Document
    Properties:
      Content: '{"description":"test"}'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3051.validate_template(&tmpl, &ast);
        assert!(!issues.is_empty());
        assert!(issues.iter().any(|i| i.message.contains("schemaVersion")));
    }

    #[test]
    fn test_function_skipped() {
        let yaml = br#"
Resources:
  MyDoc:
    Type: AWS::SSM::Document
    Properties:
      Content: !Sub '{"schemaVersion":"2.2"}'
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3051.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_inline_object_valid() {
        let yaml = br#"
Resources:
  MyDoc:
    Type: AWS::SSM::Document
    Properties:
      Content:
        schemaVersion: "2.2"
        description: test
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3051.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_inline_object_missing_schema_version() {
        let yaml = br#"
Resources:
  MyDoc:
    Type: AWS::SSM::Document
    Properties:
      Content:
        description: test
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3051.validate_template(&tmpl, &ast);
        assert!(!issues.is_empty());
        assert!(issues.iter().any(|i| i.message.contains("schemaVersion")));
    }
}

crate::register_cfn_lint_rule!(E3051);
