use std::collections::HashSet;

use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct W7001;

impl CfnLintRule for W7001 {
    fn id(&self) -> &str {
        "W7001"
    }
    fn short_description(&self) -> &str {
        "Check if Mappings are used"
    }
    fn description(&self) -> &str {
        "Check that each mapping defined in the template is referenced by Fn::FindInMap"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        if template.mappings.is_empty() {
            return vec![];
        }

        // Check if Mappings section itself is a transform
        if let Some(AstNode::Function(func)) = root.get("Mappings") {
            if func.name == "Fn::Transform" {
                return vec![];
            }
        }

        let referenced = match collect_findinmap_names(root) {
            Some(names) => names,
            None => return vec![], // dynamic mapping name — can't determine usage
        };

        template
            .mappings
            .keys()
            .filter(|name| !referenced.contains(name.as_str()))
            .map(|name| ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!("Mapping '{}' is defined but not used", name),
                path: vec!["Mappings".to_string(), name.clone()],
                span: Default::default(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
})
            .collect()
    }
}

/// Collect mapping names referenced by Fn::FindInMap throughout the AST.
/// Returns None if any FindInMap uses a dynamic (function) first argument,
/// meaning we can't determine which mappings are used.
fn collect_findinmap_names(root: &AstNode) -> Option<HashSet<String>> {
    let mut names = HashSet::new();
    let mut has_dynamic = false;
    ast::walk(root, &[], &mut |node, _path| {
        if let AstNode::Function(func) = node {
            if func.name == "Fn::FindInMap" {
                if let Some(arr) = func.args.as_array() {
                    if let Some(first) = arr.elements.first() {
                        if let Some(map_name) = first.as_str() {
                            names.insert(map_name.to_string());
                        } else if first.as_function().is_some() {
                            has_dynamic = true;
                        }
                    }
                }
            }
        }
        true
    });
    if has_dynamic { None } else { Some(names) }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_mapping_used() {
        let yaml = br#"
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, us-east-1, AMI]
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W7001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_mapping_unused() {
        let yaml = br#"
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W7001.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("W7001"));
        assert!(issues[0].message.contains("RegionMap"));
    }
}

crate::register_cfn_lint_rule!(W7001);
