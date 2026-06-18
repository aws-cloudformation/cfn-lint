use std::collections::BTreeSet;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3039: Verify the set of Attributes in AttributeDefinitions and KeySchemas match.
pub struct E3039;

impl CfnLintRule for E3039 {
    fn id(&self) -> &str {
        "E3039"
    }
    fn short_description(&self) -> &str {
        "AttributeDefinitions / KeySchemas mismatch"
    }
    fn description(&self) -> &str {
        "Verify the set of Attributes in AttributeDefinitions and KeySchemas match"
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
        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::DynamoDB::Table" {
                continue;
            }
            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            // Skip if properties contain Fn::Transform (dynamically modified)
            if contains_transform(props) {
                continue;
            }

            let attributes = collect_attribute_definitions(props);
            let keys = collect_key_schema_attrs(props);

            if attributes != keys && !attributes.is_empty() {
                let path = vec![
                    "Resources".to_string(),
                    name.to_string(),
                    "Properties".to_string(),
                ];
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "The set of Attributes in AttributeDefinitions: {:?} and KeySchemas: {:?} must match at {}",
                        attributes.iter().collect::<Vec<_>>(),
                        keys.iter().collect::<Vec<_>>(),
                        path.join("/"),
                    ),
                    path,
                    span: props.span().clone(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
});
            }
        }
        issues
    }
}

fn collect_attribute_definitions(props: &AstNode) -> BTreeSet<String> {
    let mut attrs = BTreeSet::new();
    if let Some(defs) = props.get("AttributeDefinitions").and_then(|n| n.as_array()) {
        for item in &defs.elements {
            if let Some(name) = item.get("AttributeName").and_then(|n| n.as_str()) {
                attrs.insert(name.to_string());
            }
        }
    }
    attrs
}

fn collect_key_schema_attrs(props: &AstNode) -> BTreeSet<String> {
    let mut keys = BTreeSet::new();
    // Primary key schema
    keys.extend(extract_key_schema(props.get("KeySchema")));
    // Global secondary indexes
    if let Some(gsi) = props
        .get("GlobalSecondaryIndexes")
        .and_then(|n| n.as_array())
    {
        for idx in &gsi.elements {
            keys.extend(extract_key_schema(idx.get("KeySchema")));
        }
    }
    // Local secondary indexes
    if let Some(lsi) = props
        .get("LocalSecondaryIndexes")
        .and_then(|n| n.as_array())
    {
        for idx in &lsi.elements {
            keys.extend(extract_key_schema(idx.get("KeySchema")));
        }
    }
    keys
}

fn extract_key_schema(node: Option<&AstNode>) -> BTreeSet<String> {
    let mut keys = BTreeSet::new();
    if let Some(arr) = node.and_then(|n| n.as_array()) {
        for item in &arr.elements {
            if let Some(name) = item.get("AttributeName").and_then(|n| n.as_str()) {
                keys.insert(name.to_string());
            }
        }
    }
    keys
}

fn contains_transform(node: &AstNode) -> bool {
    match node {
        AstNode::Function(f) if f.name == "Fn::Transform" => true,
        AstNode::Object(obj) => obj.iter().any(|(_, v)| contains_transform(v)),
        AstNode::Array(arr) => arr.elements.iter().any(contains_transform),
        AstNode::Function(f) => contains_transform(&f.args),
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_matching_attributes_and_keys() {
        let yaml = br#"
Resources:
  MyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: my-table
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3039.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_mismatched_attributes_and_keys() {
        let yaml = br#"
Resources:
  MyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: my-table
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: extra
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3039.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3039"));
        assert!(issues[0].message.contains("AttributeDefinitions"));
        assert!(issues[0].message.contains("KeySchemas"));
    }
}

crate::register_cfn_lint_rule!(E3039);
