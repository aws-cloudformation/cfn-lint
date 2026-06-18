use crate::ast::AstNode;

const SAM_TRANSFORM: &str = "AWS::Serverless-2016-10-31";

static SERVERLESS_RESOURCE_TYPES: &[&str] = &[
    "AWS::Serverless::Function",
    "AWS::Serverless::Api",
    "AWS::Serverless::HttpApi",
    "AWS::Serverless::SimpleTable",
    "AWS::Serverless::LayerVersion",
    "AWS::Serverless::Application",
    "AWS::Serverless::StateMachine",
];

/// Returns the known SAM resource types.
pub fn get_serverless_resource_types() -> &'static [&'static str] {
    SERVERLESS_RESOURCE_TYPES
}

/// Check if the template root has a SAM transform.
pub fn is_sam_template(root: &AstNode) -> bool {
    match root.get("Transform") {
        Some(AstNode::String(s)) => s.value == SAM_TRANSFORM,
        Some(AstNode::Array(arr)) => arr.elements.iter().any(|e| e.as_str() == Some(SAM_TRANSFORM)),
        _ => false,
    }
}

/// Check if a resource type is a SAM serverless type.
pub fn is_serverless_type(resource_type: &str) -> bool {
    resource_type.starts_with("AWS::Serverless::")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use indexmap::IndexMap;

    #[test]
    fn test_is_sam_template_string_transform() {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Transform".to_string(), span: Span::default() }),
            key: "Transform".to_string(),
            value: AstNode::String(StringNode {
                value: "AWS::Serverless-2016-10-31".to_string(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let root = AstNode::Object(ObjectNode { entries: props, span: Span::default()  });
        assert!(is_sam_template(&root));
    }

    #[test]
    fn test_is_sam_template_array_transform() {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Transform".to_string(), span: Span::default() }),
            key: "Transform".to_string(),
            value: AstNode::Array(ArrayNode {
                elements: vec![
                    AstNode::String(StringNode {
                        value: "AWS::Serverless-2016-10-31".to_string(),
                        span: Span::default(),
                    }),
                    AstNode::String(StringNode {
                        value: "AWS::Other-Transform".to_string(),
                        span: Span::default(),
                    }),
                ],
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let root = AstNode::Object(ObjectNode { entries: props, span: Span::default()  });
        assert!(is_sam_template(&root));
    }

    #[test]
    fn test_is_not_sam_template() {
        let mut props: Vec<ObjectEntry> = Vec::new();
        props.push(ObjectEntry {
            key_node: AstNode::String(StringNode { value: "Transform".to_string(), span: Span::default() }),
            key: "Transform".to_string(),
            value: AstNode::String(StringNode {
                value: "AWS::Other-Transform".to_string(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let root = AstNode::Object(ObjectNode { entries: props, span: Span::default()  });
        assert!(!is_sam_template(&root));
    }

    #[test]
    fn test_is_not_sam_template_no_transform() {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default(),
         });
        assert!(!is_sam_template(&root));
    }

    #[test]
    fn test_get_serverless_resource_types() {
        let types = get_serverless_resource_types();
        assert_eq!(types.len(), 7);
        assert!(types.contains(&"AWS::Serverless::Function"));
        assert!(types.contains(&"AWS::Serverless::StateMachine"));
    }

    #[test]
    fn test_is_serverless_type() {
        assert!(is_serverless_type("AWS::Serverless::Function"));
        assert!(is_serverless_type("AWS::Serverless::Api"));
        assert!(!is_serverless_type("AWS::S3::Bucket"));
        assert!(!is_serverless_type("Custom::MyResource"));
    }
}
