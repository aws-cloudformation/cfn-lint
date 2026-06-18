use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// W1100: Validate if the template is using YAML merge keys (<<).
pub struct W1100;

impl CfnLintRule for W1100 {
    fn id(&self) -> &str {
        "W1100"
    }
    fn short_description(&self) -> &str {
        "Validate if the template is using YAML merge"
    }
    fn description(&self) -> &str {
        "The CloudFormation service does not support YAML anchors, aliases, or merging. \
         This rule validates if the merge capability is being used"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        ast::walk(root, &[], &mut |node, path| {
            if let Some(obj) = node.as_object() {
                if let Some(merge_node) = obj.get("<<") {
                    issues.push(ValidationError {
                        rule_id: Some("W1100".to_string()),
                        message: "YAML merge key '<<' is not supported by CloudFormation"
                            .to_string(),
                        path: {
                            let mut p = path.to_vec();
                            p.push("<<".to_string());
                            p
                        },
                        span: merge_node.span().clone(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                }
            }
            true
        });
        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use crate::parser;
    use indexmap::IndexMap;

    #[test]
    fn test_no_merge_key() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1100.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_merge_key_detected() {
        // Build AST manually since serde_yaml resolves merge keys
        let mut merge_props: Vec<ObjectEntry> = Vec::new();
        merge_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "<<".to_string(), span: Span::default() }),
            key: "<<".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: vec![ObjectEntry {
                    key_node: AstNode::String(StringNode { value: "Key".to_string(), span: Span::default() }),
                    key: "Key".to_string(),
                    value: AstNode::String(StringNode {
                        value: "val".to_string(),
                        span: Span { start: Position { line: 3, column: 5 }, end: Position { line: 3, column: 5 } },
                    }),
                    key_span: Span::default(),
                }],
                span: Span { start: Position { line: 3, column: 3 }, end: Position { line: 3, column: 3 } },
            }),
            key_span: Span::default(),
        });
        let mut res_props: Vec<ObjectEntry> = Vec::new();
        res_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Type".to_string(), span: Span::default() }),
            key: "Type".to_string(),
            value: AstNode::String(StringNode {
                value: "AWS::S3::Bucket".to_string(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        res_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Properties".to_string(), span: Span::default() }),
            key: "Properties".to_string(),
            value: AstNode::Object(ObjectNode { entries: merge_props, span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let mut resources: Vec<ObjectEntry> = Vec::new();
        resources.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Bucket".to_string(), span: Span::default() }),
            key: "Bucket".to_string(),
            value: AstNode::Object(ObjectNode { entries: res_props, span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let mut root_props: Vec<ObjectEntry> = Vec::new();
        root_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Resources".to_string(), span: Span::default() }),
            key: "Resources".to_string(),
            value: AstNode::Object(ObjectNode { entries: resources, span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let root = AstNode::Object(ObjectNode { entries: root_props, span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        let issues = W1100.validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("W1100"));
        assert!(issues[0].message.contains("<<"));
    }
}

crate::register_cfn_lint_rule!(W1100);
