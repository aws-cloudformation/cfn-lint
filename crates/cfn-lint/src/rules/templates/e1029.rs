use std::sync::LazyLock;

use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1029;

/// Matches `${...}` substitution variables. Hoisted to a static so the regex
/// is compiled once rather than on every call to `validate_template` (C58).
static SUB_VAR_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\$\{[A-Za-z0-9_:\.]+\}").unwrap());

const PSEUDO_PARAMS: &[&str] = &[
    "AWS::AccountId",
    "AWS::NotificationARNs",
    "AWS::NoValue",
    "AWS::Partition",
    "AWS::Region",
    "AWS::StackId",
    "AWS::StackName",
    "AWS::URLSuffix",
];

impl CfnLintRule for E1029 {
    fn id(&self) -> &str {
        "E1029"
    }

    fn short_description(&self) -> &str {
        "Sub is required if a variable is used in a string"
    }

    fn description(&self) -> &str {
        "If a substitution variable exists in a string but isn't wrapped with Fn::Sub the deployment will fail"
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
        let mut issues = Vec::new();
        self.check_node(root, &[], &SUB_VAR_RE, template, root, &mut issues);
        issues
    }
}

impl E1029 {
    fn is_known_variable(&self, var_name: &str, template: &Template) -> bool {
        if PSEUDO_PARAMS.contains(&var_name) {
            return true;
        }
        if template.parameters.contains_key(var_name) {
            return true;
        }
        if template.resources.contains_key(var_name) {
            return true;
        }
        if let Some(dot_pos) = var_name.find('.') {
            let resource_name = &var_name[..dot_pos];
            if template.resources.contains_key(resource_name) {
                return true;
            }
        }
        false
    }

    fn path_contains_definition_string(path: &[String]) -> bool {
        path.iter()
            .any(|p| p == "DefinitionString" || p == "Definition")
    }

    fn is_in_definition_substitutions(
        &self,
        var_name: &str,
        path: &[String],
        root: &AstNode,
    ) -> bool {
        for key in &["DefinitionString", "Definition"] {
            if let Some(idx) = path.iter().position(|p| p == *key) {
                let mut sub_path: Vec<&str> = path[..idx].iter().map(|s| s.as_str()).collect();
                sub_path.push("DefinitionSubstitutions");
                sub_path.push(var_name);
                let mut node = root;
                for seg in &sub_path {
                    match node.get(seg) {
                        Some(n) => node = n,
                        None => return false,
                    }
                }
                return true;
            }
        }
        false
    }

    fn check_node(
        &self,
        node: &AstNode,
        path: &[String],
        re: &Regex,
        template: &Template,
        root: &AstNode,
        issues: &mut Vec<ValidationError>,
    ) {
        match node {
            AstNode::Function(func) => {
                // Fn::Sub handles the variables in its own template string, but
                // the values of its substitution map must still be checked
                // (C61). For the array form ["template", {map}], recurse into
                // the map values (element [1]); the template string (element
                // [0]) is intentionally skipped.
                if func.name == "Fn::Sub" {
                    if let AstNode::Array(arr) = func.args.as_ref() {
                        if arr.elements.len() == 2 {
                            let mut child_path = path.to_vec();
                            child_path.push(func.name.clone());
                            child_path.push("1".to_string());
                            self.check_node(
                                &arr.elements[1],
                                &child_path,
                                re,
                                template,
                                root,
                                issues,
                            );
                        }
                    }
                    return;
                }
                // Include function name in path (matches Python's _match_values which sees dict keys)
                let mut child_path = path.to_vec();
                child_path.push(func.name.clone());
                self.check_node(&func.args, &child_path, re, template, root, issues);
            }
            AstNode::String(s) => {
                // Skip TemplateBody exception
                if path.last().is_some_and(|p| p == "TemplateBody") {
                    return;
                }
                for m in re.find_iter(&s.value) {
                    let var = m.as_str();
                    if var.starts_with("${!") {
                        continue;
                    }
                    if var.starts_with("${stageVariables.") {
                        continue;
                    }
                    let var_name = &var[2..var.len() - 1];

                    if self.is_in_definition_substitutions(var_name, path, root) {
                        continue;
                    }

                    let in_definition_string = Self::path_contains_definition_string(path);

                    // Flag if it's a known ref OR if we're in DefinitionString context
                    if self.is_known_variable(var_name, template) || in_definition_string {
                        issues.push(ValidationError {
                            rule_id: Some("E1029".to_string()),
                            message: format!(
                                "Found an embedded parameter \"{}\" outside of an \"Fn::Sub\" at {}",
                                var,
                                path.join("/")
                            ),
                            path: path.to_vec(),
                            span: s.span,
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
});
                    }
                }
            }
            AstNode::Object(obj) => {
                for (key, value) in obj.iter() {
                    let mut child_path = path.to_vec();
                    child_path.push(key.to_string());
                    self.check_node(value, &child_path, re, template, root, issues);
                }
            }
            AstNode::Array(arr) => {
                for (i, elem) in arr.elements.iter().enumerate() {
                    let mut child_path = path.to_vec();
                    child_path.push(i.to_string());
                    self.check_node(elem, &child_path, re, template, root, issues);
                }
            }
            _ => {}
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_no_issue_inside_sub() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::Region}-bucket"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1029.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_variable_outside_sub() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: "${AWS::Region}-bucket"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1029.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1029"));
        assert!(issues[0].message.contains("${AWS::Region}"));
    }

    #[test]
    fn test_unknown_variable_in_join_not_flagged() {
        let yaml = b"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Base64:
          Fn::Join:
            - \"\"
            - - \"#!/bin/bash\"
              - \"export PATH=${PATH}:/usr/local/bin\"
";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        // ${PATH} is not a known ref, so it should NOT be flagged
        assert!(E1029.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_known_variable_in_join_flagged() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Base64:
          Fn::Join:
            - ""
            - - "prefix-"
              - "${MyBucket}"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1029.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("${MyBucket}"));
    }

    #[test]
    fn test_unknown_variable_not_flagged() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: "${mtlsuri}"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1029.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_stage_variables_not_flagged() {
        let yaml = br#"
Resources:
  Api:
    Type: AWS::ApiGateway::Method
    Properties:
      Integration:
        Uri: "https://example.com/${stageVariables.env}/api"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1029.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_resource_ref_outside_sub_flagged() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
  Other:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: "${MyBucket}-name"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1029.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("${MyBucket}"));
    }

    // C61: an embedded variable in an Fn::Sub substitution-map VALUE (not the
    // template string) must still be flagged.
    #[test]
    fn test_embedded_var_in_sub_map_value_flagged() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
  Other:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub:
          - "${Prefix}-bucket"
          - Prefix: "${MyBucket}"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1029.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1, "got: {:?}", issues);
        assert!(issues[0].message.contains("${MyBucket}"));
    }

    // C61: the Fn::Sub template string itself is still not flagged (local
    // substitution variables are legitimately declared there).
    #[test]
    fn test_sub_template_string_not_flagged() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
  Other:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Sub:
          - "${MyBucket}-bucket"
          - Prefix: static
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1029.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E1029);
