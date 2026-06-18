use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W2501: Check if Password Properties are properly configured.
pub struct W2501;

const PASSWORD_PROPS: &[&str] = &[
    "AccountPassword",
    "AdminPassword",
    "ADDomainJoinPassword",
    "CrossRealmTrustPrincipalPassword",
    "KdcAdminPassword",
    "Password",
    "DbPassword",
    "MasterUserPassword",
    "PasswordParam",
];

impl CfnLintRule for W2501 {
    fn id(&self) -> &str {
        "W2501"
    }
    fn short_description(&self) -> &str {
        "Check if Password Properties are correctly configured"
    }
    fn description(&self) -> &str {
        "Password properties should not be strings and if parameter using NoEcho"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let dyn_ref = Regex::new(r"\{\{resolve:").unwrap();
        let ssm_ref = Regex::new(r"\{\{resolve:ssm:").unwrap();
        let mut issues = Vec::new();

        for (name, _resource) in &template.resources {
            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };
            for &pwd_prop in PASSWORD_PROPS {
                self.check_password(
                    props,
                    pwd_prop,
                    name,
                    template,
                    &dyn_ref,
                    &ssm_ref,
                    &mut issues,
                );
            }
        }
        issues
    }
}

impl W2501 {
    fn check_password(
        &self,
        props: &AstNode,
        pwd_prop: &str,
        res_name: &str,
        template: &Template,
        dyn_ref: &Regex,
        ssm_ref: &Regex,
        issues: &mut Vec<ValidationError>,
    ) {
        let node = match props.get(pwd_prop) {
            Some(n) => n,
            None => return,
        };
        let path = vec![
            "Resources".into(),
            res_name.to_string(),
            "Properties".into(),
            pwd_prop.to_string(),
        ];
        match node {
            AstNode::String(s) => {
                if dyn_ref.is_match(&s.value) {
                    if ssm_ref.is_match(&s.value) {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "Password should use a secure dynamic reference for {}",
                                path.join("/")
                            ),
                            path: path.clone(),
                            span: s.span.clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                } else {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!("Password shouldn't be hardcoded for {}", path.join("/")),
                        path,
                        span: s.span.clone(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
            AstNode::Function(func) if func.name == "Ref" => {
                if let Some(param_name) = func.args.as_str() {
                    if let Some(param) = template.get_parameter(param_name) {
                        if !param.no_echo {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "Parameter {} used as {}, therefore NoEcho should be True",
                                    param_name, pwd_prop
                                ),
                                path: vec!["Parameters".into(), param_name.to_string()],
                                span: func.span.clone(),
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
            _ => {}
        }
    }
}

crate::register_cfn_lint_rule!(W2501);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_password_with_secrets_manager_ok() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUserPassword: "{{resolve:secretsmanager:my-secret}}"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2501.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_hardcoded_password_warns() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      MasterUserPassword: "plaintext123"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W2501.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("hardcoded"));
    }
}
