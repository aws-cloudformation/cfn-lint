use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E5001: Check that Modules resources are valid.
///
/// Validates that MODULE resources do not use CreationPolicy, UpdatePolicy,
/// or Tags, and that the reserved metadata key AWS::CloudFormation::Module
/// is not used.
pub struct E5001;

impl CfnLintRule for E5001 {
    fn id(&self) -> &str { "E5001" }
    fn short_description(&self) -> &str { "Check that Modules resources are valid" }
    fn description(&self) -> &str {
        "Validates that MODULE resources do not use CreationPolicy, \
         UpdatePolicy, or Tags"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let resources = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let mut issues = Vec::new();
        for (name, node) in resources.iter() {
            let obj = match node.as_object() {
                Some(o) => o,
                None => continue,
            };
            let rtype = match obj.get("Type").and_then(|t| t.as_str()) {
                Some(t) => t,
                None => continue,
            };
            if !rtype.ends_with("::MODULE") {
                continue;
            }

            for policy in &["CreationPolicy", "UpdatePolicy"] {
                if obj.contains_key(*policy) {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!("{} is not permitted within Modules", policy),
                        path: vec!["Resources".into(), name.to_string(), policy.to_string()],
                        span: node.span(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                }
            }

            if let Some(props) = obj.get("Properties").and_then(|p| p.as_object()) {
                if props.contains_key("Tags") {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: "Tags is not permitted within Modules".to_string(),
                        path: vec!["Resources".into(), name.to_string(), "Properties".into(), "Tags".into()],
                        span: node.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                    schema_id: None,
                    });
                }
            }
        }

        // Check for reserved metadata key across all MODULE resources
        let module_names: Vec<&str> = resources.iter()
            .filter(|(_, v)| v.as_object()
                .and_then(|o| o.get("Type"))
                .and_then(|t| t.as_str())
                .map_or(false, |t| t.ends_with("::MODULE")))
            .map(|(n, _)| n)
            .collect();
        if !module_names.is_empty() {
            for (name, node) in resources.iter() {
                if let Some(metadata) = node.as_object()
                    .and_then(|o| o.get("Metadata"))
                    .and_then(|m| m.as_object())
                {
                    if module_names.contains(&name)
                        && metadata.contains_key("AWS::CloudFormation::Module")
                    {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: "The Metadata key AWS::CloudFormation::Module is reserved".to_string(),
                            path: vec!["Resources".into(), name.to_string(), "Metadata".into(), "AWS::CloudFormation::Module".into()],
                            span: node.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                        schema_id: None,
                        });
                    }
                }
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
    fn test_valid_module() {
        let yaml = br#"
Resources:
  MyModule:
    Type: My::Testing::MODULE
    Properties:
      Param1: value1
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E5001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_module_with_creation_policy() {
        let yaml = br#"
Resources:
  MyModule:
    Type: My::Testing::MODULE
    CreationPolicy:
      ResourceSignal:
        Count: 1
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E5001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("CreationPolicy"));
    }
}

crate::register_cfn_lint_rule!(E5001);
