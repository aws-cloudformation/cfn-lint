use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E1002;

impl CfnLintRule for E1002 {
    fn id(&self) -> &str {
        "E1002"
    }

    fn short_description(&self) -> &str {
        "Template must be a valid object"
    }

    fn description(&self) -> &str {
        "Check that the root of the template is a mapping/object"
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
        if root.as_object().is_some() {
            vec![]
        } else {
            vec![ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!("Template root must be an object, got {}", root.node_type()),
                path: vec![],
                span: root.span().clone(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }]
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use indexmap::IndexMap;

    #[test]
    fn test_valid_object_root() {
        let root = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        assert!(E1002.validate_template(&tmpl, &root).is_empty());
    }

    #[test]
    fn test_string_root() {
        let root = AstNode::String(StringNode {
            value: "not a template".to_string(),
            span: Span {
                start: Position { line: 1, column: 1 },
                end: Position { line: 1, column: 1 },
            },
        });
        // Template::from_ast will fail on non-object, so we build a dummy template
        let dummy = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&dummy).unwrap();
        let issues = E1002.validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1002"));
        assert!(issues[0].message.contains("string"));
    }

    #[test]
    fn test_array_root() {
        let root = AstNode::Array(ArrayNode {
            elements: vec![],
            span: Span {
                start: Position { line: 1, column: 1 },
                end: Position { line: 1, column: 1 },
            },
        });
        let dummy = AstNode::Object(ObjectNode {
            entries: Vec::new(),
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&dummy).unwrap();
        let issues = E1002.validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("array"));
    }
}

crate::register_cfn_lint_rule!(E1002);
