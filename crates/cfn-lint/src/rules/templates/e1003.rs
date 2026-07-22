use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1003;

impl CfnLintRule for E1003 {
    fn id(&self) -> &str {
        "E1003"
    }

    fn short_description(&self) -> &str {
        "Template description limit"
    }

    fn description(&self) -> &str {
        "Check if the template description exceeds the 1024 character limit"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        if let Some(AstNode::String(desc)) = root.get("Description") {
            if desc.value.len() > 1024 {
                return vec![ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "Template description must be no longer than 1024 characters (current: {})",
                        desc.value.len()
                    ),
                    path: vec!["Description".to_string()],
                    span: desc.span,
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectEntry, ObjectNode, Position, Span, StringNode};

    fn make_template_with_description(desc: &str) -> (Template, AstNode) {
        let props: Vec<ObjectEntry> = vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Description".to_string(),
                span: Span::default(),
            }),
            key: "Description".to_string(),
            value: AstNode::String(StringNode {
                value: desc.to_string(),
                span: Span {
                    start: Position { line: 2, column: 1 },
                    end: Position { line: 2, column: 1 },
                },
            }),
            key_span: Span::default(),
        }];
        let root = AstNode::Object(ObjectNode {
            entries: props,
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        (tmpl, root)
    }

    #[test]
    fn test_valid_description() {
        let (tmpl, root) = make_template_with_description("Short description");
        let issues = E1003.validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_description_too_long() {
        let long = "x".repeat(1025);
        let (tmpl, root) = make_template_with_description(&long);
        let issues = E1003.validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1003"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1003"));
        assert_eq!(issues[0].path, vec!["Description"]);
        assert!(issues[0].message.contains("1025"));
    }

    #[test]
    fn test_description_exactly_1024() {
        let exact = "x".repeat(1024);
        let (tmpl, root) = make_template_with_description(&exact);
        let issues = E1003.validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_no_description() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        let issues = E1003.validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }
}

crate::register_cfn_lint_rule!(E1003);
