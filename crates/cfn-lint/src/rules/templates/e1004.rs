use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct E1004;

impl CfnLintRule for E1004 {
    fn id(&self) -> &str {
        "E1004"
    }

    fn short_description(&self) -> &str {
        "Template description must be a string"
    }

    fn description(&self) -> &str {
        "Check if the template description is a string type"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        if let Some(desc) = root.get("Description") {
            if !matches!(desc, AstNode::String(_)) {
                return vec![ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "Template description must be a string, got {}",
                        desc.node_type()
                    ),
                    path: vec!["Description".to_string()],
                    span: desc.span().clone(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
}];
            }
        }
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1004);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

    #[test]
    fn test_valid_string_description() {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Description".to_string(), span: Span::default() }),
            key: "Description".to_string(),
            value: AstNode::String(StringNode {
                value: "A valid description".to_string(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let root = AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1004.validate_template(&tmpl, &root).is_empty());
    }

    #[test]
    fn test_number_description() {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Description".to_string(), span: Span::default() }),
            key: "Description".to_string(),
            value: AstNode::Number(NumberNode {
                value: 42.0,
                span: Span { start: Position { line: 2, column: 1 }, end: Position { line: 2, column: 1 } },
            }),
            key_span: Span::default(),
        });
        let root = AstNode::Object(ObjectNode { entries: props, span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        let issues = E1004.validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1004"));
        assert!(issues[0].message.contains("integer"));
    }

    #[test]
    fn test_no_description() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1004.validate_template(&tmpl, &root).is_empty());
    }
}
