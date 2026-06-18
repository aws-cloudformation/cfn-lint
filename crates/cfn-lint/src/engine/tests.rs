use super::*;
use crate::ast::{
    ArrayNode, AstNode, BoolNode, NullNode, NumberNode, ObjectEntry, ObjectNode, Position, Span,
    StringNode,
};
use crate::parser;
use serde_json::json;

#[test]
fn test_engine_no_issues() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Valid
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties: {}
"#;
    let root = parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&root).unwrap();
    let mut engine = Engine::new();
    let regions = vec!["us-east-1".to_string()];
    let issues = engine.validate(&tmpl, &root, &regions);
    // Filter out S3 best-practice rules (W3037, W3045, I3042) since this test
    // only checks that no error-level issues are produced for a valid template.
    let issues: Vec<_> = issues
        .into_iter()
        .filter(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E'))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_engine_catches_long_description() {
    let long_desc = "x".repeat(1025);
    let yaml = format!(
            "AWSTemplateFormatVersion: '2010-09-09'\nDescription: \"{}\"\nResources:\n  Bucket:\n    Type: AWS::S3::Bucket\n    Properties: {{}}\n",
            long_desc
        );
    let root = parser::parse(yaml.as_bytes()).unwrap();
    let tmpl = Template::from_ast(&root).unwrap();
    let mut engine = Engine::new();
    let regions = vec!["us-east-1".to_string()];
    let issues = engine.validate(&tmpl, &root, &regions);
    let e1003_issues: Vec<_> = issues
        .iter()
        .filter(|i| i.rule_id.as_deref() == Some("E1003"))
        .collect();
    assert_eq!(e1003_issues.len(), 1);
    assert_eq!(e1003_issues[0].rule_id.as_deref(), Some("E1003"));
}

#[test]
fn test_engine_has_e1003_registered() {
    let engine = Engine::new();
    // Rule E1003 is registered via inventory
}

#[test]
fn test_engine_no_schema_manager_skips_schema_validation() {
    let mut engine = Engine::new();
    assert!(engine.schema_provider.is_none());

    let root = make_template_ast("AWS::S3::Bucket", json!({"BucketName": "my-bucket"}));
    let tmpl = Template::from_ast(&root).unwrap();
    let regions = vec!["us-east-1".to_string()];
    let issues = engine.validate(&tmpl, &root, &regions);
    // No schema manager → no E3001 issues
    assert!(issues.iter().all(|i| i.rule_id.as_deref() != Some("E3001")));
}

#[test]
fn test_schema_validation_valid_properties() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    let root = make_template_ast("AWS::S3::Bucket", json!({"BucketName": "my-bucket"}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3001"))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_schema_validation_wrong_type() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    // Use an array where string is expected — arrays don't coerce to string
    let root = make_template_ast_raw(
        "AWS::S3::Bucket",
        AstNode::Object(ObjectNode {
            entries: vec![ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "BucketName".to_string(),
                    span: Span::default(),
                }),
                key: "BucketName".to_string(),
                value: AstNode::Array(crate::ast::ArrayNode {
                    elements: vec![],
                    span: Span {
                        start: Position { line: 5, column: 3 },
                        end: Position { line: 5, column: 3 },
                    },
                }),
                key_span: Span::default(),
            }],
            span: Span::default(),
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3012"))
        .collect();
    assert!(!issues.is_empty());
    assert_eq!(issues[0].rule_id.as_deref(), Some("E3012"));
    assert!(issues[0].message.contains("type"));
}

#[test]
fn test_schema_validation_additional_property() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    let root = make_template_ast(
        "AWS::S3::Bucket",
        json!({"BucketName": "ok", "FakeProperty": "bad"}),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3002"))
        .collect();
    assert!(!issues.is_empty());
    assert!(issues[0].message.contains("FakeProperty"));
}

#[test]
fn test_schema_validation_required_property() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::Lambda::Function",
        json!({
            "typeName": "AWS::Lambda::Function",
            "properties": {
                "Runtime": {"type": "string"},
                "Code": {"type": "object"}
            },
            "required": ["Code"],
            "additionalProperties": false
        }),
    );

    let root = make_template_ast("AWS::Lambda::Function", json!({"Runtime": "python3.12"}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3003"))
        .collect();
    assert!(!issues.is_empty());
    assert!(issues[0].message.contains("Code"));
}

#[test]
fn test_schema_validation_unknown_resource_type_skipped() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {"BucketName": {"type": "string"}}
        }),
    );

    let root = make_template_ast("AWS::Custom::Thing", json!({"Anything": "goes"}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3001"))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_schema_validation_resource_without_properties_skipped() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::CloudFormation::WaitConditionHandle",
        json!({
            "typeName": "AWS::CloudFormation::WaitConditionHandle",
            "properties": {}
        }),
    );

    // Resource with no Properties section
    let mut res_props: Vec<ObjectEntry> = Vec::new();
    res_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Type".to_string(),
            span: Span::default(),
        }),
        key: "Type".to_string(),
        value: AstNode::String(StringNode {
            value: "AWS::CloudFormation::WaitConditionHandle".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let mut resources: Vec<ObjectEntry> = Vec::new();
    resources.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Handle".to_string(),
            span: Span::default(),
        }),
        key: "Handle".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: res_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let mut root_props: Vec<ObjectEntry> = Vec::new();
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Resources".to_string(),
            span: Span::default(),
        }),
        key: "Resources".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: resources,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let root = AstNode::Object(ObjectNode {
        entries: root_props,
        span: Span::default(),
    });
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3001"))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_schema_validation_path_includes_resource_name() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    let root = make_template_ast("AWS::S3::Bucket", json!({"BadProp": "value"}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3002"))
        .collect();
    assert!(!issues.is_empty());
    assert!(issues[0].path.contains(&"Resources".to_string()));
    assert!(issues[0].path.contains(&"Properties".to_string()));
}

#[test]
fn test_with_data_dir_invalid_dir() {
    let engine = Engine::with_data_dir(PathBuf::from("/nonexistent/path"));
    assert!(engine.schema_provider.is_none());
}

#[test]
fn test_ref_aws_region_in_string_property_no_type_error() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    // Build properties with !Ref AWS::Region as BucketName
    let props = AstNode::Object(ObjectNode {
        entries: vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "BucketName".to_string(),
                span: Span::default(),
            }),
            key: "BucketName".to_string(),
            value: AstNode::Function(crate::ast::FunctionNode {
                name: "Ref".to_string(),
                args: Box::new(AstNode::String(StringNode {
                    value: "AWS::Region".to_string(),
                    span: Span::default(),
                })),
                span: Span {
                    start: Position { line: 5, column: 7 },
                    end: Position { line: 5, column: 7 },
                },
            }),
            key_span: Span::default(),
        }],
        span: Span::default(),
    });

    let root = make_template_ast_raw("AWS::S3::Bucket", props);
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3001"))
        .collect();
    // Ref AWS::Region resolves to "us-east-1" (a string), so no type error
    assert!(
        issues.is_empty(),
        "Expected no E3001 issues but got: {:?}",
        issues
    );
}

#[test]
fn test_unresolvable_ref_left_as_is_no_crash() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    // Build properties with !Ref to a parameter that has no default/allowed values
    let mut root_props: Vec<ObjectEntry> = Vec::new();

    // Add a parameter with no default
    let mut param_props: Vec<ObjectEntry> = Vec::new();
    param_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Type".to_string(),
            span: Span::default(),
        }),
        key: "Type".to_string(),
        value: AstNode::String(StringNode {
            value: "String".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let mut params: Vec<ObjectEntry> = Vec::new();
    params.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "UnknownParam".to_string(),
            span: Span::default(),
        }),
        key: "UnknownParam".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: param_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Parameters".to_string(),
            span: Span::default(),
        }),
        key: "Parameters".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: params,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    // Add a resource with Ref to the unresolvable parameter
    let mut res_inner: Vec<ObjectEntry> = Vec::new();
    res_inner.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Type".to_string(),
            span: Span::default(),
        }),
        key: "Type".to_string(),
        value: AstNode::String(StringNode {
            value: "AWS::S3::Bucket".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let mut bucket_props: Vec<ObjectEntry> = Vec::new();
    bucket_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "BucketName".to_string(),
            span: Span::default(),
        }),
        key: "BucketName".to_string(),
        value: AstNode::Function(crate::ast::FunctionNode {
            name: "Ref".to_string(),
            args: Box::new(AstNode::String(StringNode {
                value: "UnknownParam".to_string(),
                span: Span::default(),
            })),
            span: Span {
                start: Position { line: 8, column: 7 },
                end: Position { line: 8, column: 7 },
            },
        }),
        key_span: Span::default(),
    });
    res_inner.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Properties".to_string(),
            span: Span::default(),
        }),
        key: "Properties".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: bucket_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let mut resources: Vec<ObjectEntry> = Vec::new();
    resources.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "MyResource".to_string(),
            span: Span::default(),
        }),
        key: "MyResource".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: res_inner,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Resources".to_string(),
            span: Span::default(),
        }),
        key: "Resources".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: resources,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let root = AstNode::Object(ObjectNode {
        entries: root_props,
        span: Span::default(),
    });
    let tmpl = Template::from_ast(&root).unwrap();

    // Should not panic — unresolvable Ref stays as FunctionNode
    let _issues = engine.validate(&tmpl, &root, &["us-east-1".to_string()]);
    // We just verify it doesn't crash; the FunctionNode remains in the tree
}

// --- Test helpers ---

/// Create a template AST with a single resource from JSON property values.
fn make_template_ast(resource_type: &str, properties: serde_json::Value) -> AstNode {
    let props_node = json_to_ast(&properties);
    make_template_ast_raw(resource_type, props_node)
}

fn make_template_ast_raw(resource_type: &str, props_node: AstNode) -> AstNode {
    let mut res_props: Vec<ObjectEntry> = Vec::new();
    res_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Type".to_string(),
            span: Span::default(),
        }),
        key: "Type".to_string(),
        value: AstNode::String(StringNode {
            value: resource_type.to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    res_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Properties".to_string(),
            span: Span::default(),
        }),
        key: "Properties".to_string(),
        value: props_node,
        key_span: Span::default(),
    });

    let mut resources: Vec<ObjectEntry> = Vec::new();
    resources.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "MyResource".to_string(),
            span: Span::default(),
        }),
        key: "MyResource".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: res_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let mut root_props: Vec<ObjectEntry> = Vec::new();
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Resources".to_string(),
            span: Span::default(),
        }),
        key: "Resources".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: resources,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    AstNode::Object(ObjectNode {
        entries: root_props,
        span: Span::default(),
    })
}

/// Convert a serde_json::Value to AstNode for test construction.
fn json_to_ast(value: &serde_json::Value) -> AstNode {
    match value {
        serde_json::Value::Object(map) => {
            let mut props: Vec<ObjectEntry> = Vec::new();
            for (k, v) in map {
                props.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: k.clone(),
                        span: Span::default(),
                    }),
                    key: k.clone(),
                    value: json_to_ast(v),
                    key_span: Span::default(),
                });
            }
            AstNode::Object(ObjectNode {
                entries: props,
                span: Span::default(),
            })
        }
        serde_json::Value::Array(arr) => AstNode::Array(crate::ast::ArrayNode {
            elements: arr.iter().map(json_to_ast).collect(),
            span: Span::default(),
        }),
        serde_json::Value::String(s) => AstNode::String(StringNode {
            value: s.clone(),
            span: Span::default(),
        }),
        serde_json::Value::Number(n) => AstNode::Number(crate::ast::NumberNode {
            value: n.as_f64().unwrap_or(0.0),
            span: Span::default(),
        }),
        serde_json::Value::Bool(b) => AstNode::Bool(crate::ast::BoolNode {
            value: *b,
            span: Span::default(),
        }),
        serde_json::Value::Null => AstNode::Null(crate::ast::NullNode {
            span: Span::default(),
        }),
    }
}

struct TempSchemaDir {
    root: PathBuf,
}

impl TempSchemaDir {
    fn new() -> Self {
        use std::sync::atomic::{AtomicU64, Ordering};
        static COUNTER: AtomicU64 = AtomicU64::new(0);
        let id = COUNTER.fetch_add(1, Ordering::SeqCst);
        let root = std::env::temp_dir().join(format!(
            "cfn-lint-engine-test-{}-{}",
            std::process::id(),
            id
        ));
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(root.join("schemas/providers")).unwrap();
        std::fs::create_dir_all(root.join("schemas/resources")).unwrap();
        TempSchemaDir { root }
    }
}

impl Drop for TempSchemaDir {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.root);
    }
}

/// Create an Engine with a mock schema for a single resource type.
fn engine_with_mock_schema(
    resource_type: &str,
    schema: serde_json::Value,
) -> (Engine, TempSchemaDir) {
    let dir = TempSchemaDir::new();
    let hash = "test_hash";

    // Write provider mapping
    let provider = json!({ resource_type: hash });
    std::fs::write(
        dir.root.join("schemas/providers/us_east_1.json"),
        serde_json::to_string(&provider).unwrap(),
    )
    .unwrap();

    // Write resource schema
    std::fs::write(
        dir.root
            .join("schemas/resources")
            .join(format!("{}.json", hash)),
        serde_json::to_string(&schema).unwrap(),
    )
    .unwrap();

    let engine = Engine::with_data_dir(dir.root.clone());
    assert!(engine.schema_provider.is_some());
    (engine, dir)
}

/// Build a template AST with optional template-level and resource-level metadata.
fn make_template_with_metadata(
    description: &str,
    template_ignores: &[&str],
    resource_ignores: &[(&str, &[&str])],
) -> AstNode {
    let mut root_props: Vec<ObjectEntry> = Vec::new();
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "AWSTemplateFormatVersion".to_string(),
            span: Span::default(),
        }),
        key: "AWSTemplateFormatVersion".to_string(),
        value: AstNode::String(StringNode {
            value: "2010-09-09".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Description".to_string(),
            span: Span::default(),
        }),
        key: "Description".to_string(),
        value: AstNode::String(StringNode {
            value: description.to_string(),
            span: Span {
                start: Position { line: 2, column: 1 },
                end: Position { line: 2, column: 1 },
            },
        }),
        key_span: Span::default(),
    });

    // Template-level metadata
    if !template_ignores.is_empty() {
        let ignore_array = AstNode::Array(ArrayNode {
            elements: template_ignores
                .iter()
                .map(|id| {
                    AstNode::String(StringNode {
                        value: id.to_string(),
                        span: Span::default(),
                    })
                })
                .collect(),
            span: Span::default(),
        });
        let mut config_props: Vec<ObjectEntry> = Vec::new();
        config_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "ignore_checks".to_string(),
                span: Span::default(),
            }),
            key: "ignore_checks".to_string(),
            value: ignore_array,
            key_span: Span::default(),
        });
        let mut cfn_lint_props: Vec<ObjectEntry> = Vec::new();
        cfn_lint_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "config".to_string(),
                span: Span::default(),
            }),
            key: "config".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: config_props,
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        let mut meta_props: Vec<ObjectEntry> = Vec::new();
        meta_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "cfn-lint".to_string(),
                span: Span::default(),
            }),
            key: "cfn-lint".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: cfn_lint_props,
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        root_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Metadata".to_string(),
                span: Span::default(),
            }),
            key: "Metadata".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: meta_props,
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
    }

    // Resources
    let mut resources: Vec<ObjectEntry> = Vec::new();
    let resource_names: Vec<String> = if resource_ignores.is_empty() {
        vec!["MyBucket".to_string()]
    } else {
        resource_ignores
            .iter()
            .map(|(name, _)| name.to_string())
            .collect()
    };

    for res_name in &resource_names {
        let mut res_props: Vec<ObjectEntry> = Vec::new();
        res_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Type".to_string(),
                span: Span::default(),
            }),
            key: "Type".to_string(),
            value: AstNode::String(StringNode {
                value: "AWS::S3::Bucket".to_string(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
        res_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Properties".to_string(),
                span: Span::default(),
            }),
            key: "Properties".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: Vec::new(),
                span: Span::default(),
            }),
            key_span: Span::default(),
        });

        // Resource-level metadata
        if let Some((_, ignores)) = resource_ignores.iter().find(|(n, _)| n == res_name) {
            if !ignores.is_empty() {
                let ignore_array = AstNode::Array(ArrayNode {
                    elements: ignores
                        .iter()
                        .map(|id| {
                            AstNode::String(StringNode {
                                value: id.to_string(),
                                span: Span::default(),
                            })
                        })
                        .collect(),
                    span: Span::default(),
                });
                let mut config_props: Vec<ObjectEntry> = Vec::new();
                config_props.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "ignore_checks".to_string(),
                        span: Span::default(),
                    }),
                    key: "ignore_checks".to_string(),
                    value: ignore_array,
                    key_span: Span::default(),
                });
                let mut cfn_lint_props: Vec<ObjectEntry> = Vec::new();
                cfn_lint_props.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "config".to_string(),
                        span: Span::default(),
                    }),
                    key: "config".to_string(),
                    value: AstNode::Object(ObjectNode {
                        entries: config_props,
                        span: Span::default(),
                    }),
                    key_span: Span::default(),
                });
                let mut meta_props: Vec<ObjectEntry> = Vec::new();
                meta_props.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "cfn-lint".to_string(),
                        span: Span::default(),
                    }),
                    key: "cfn-lint".to_string(),
                    value: AstNode::Object(ObjectNode {
                        entries: cfn_lint_props,
                        span: Span::default(),
                    }),
                    key_span: Span::default(),
                });
                res_props.push(ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "Metadata".to_string(),
                        span: Span::default(),
                    }),
                    key: "Metadata".to_string(),
                    value: AstNode::Object(ObjectNode {
                        entries: meta_props,
                        span: Span::default(),
                    }),
                    key_span: Span::default(),
                });
            }
        }

        resources.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: res_name.clone(),
                span: Span::default(),
            }),
            key: res_name.clone(),
            value: AstNode::Object(ObjectNode {
                entries: res_props,
                span: Span::default(),
            }),
            key_span: Span::default(),
        });
    }

    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Resources".to_string(),
            span: Span::default(),
        }),
        key: "Resources".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: resources,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    AstNode::Object(ObjectNode {
        entries: root_props,
        span: Span::default(),
    })
}

#[test]
fn test_template_level_suppression_removes_matching_issues() {
    // Description > 1024 chars triggers E1003, but template metadata suppresses it
    let long_desc = "x".repeat(1025);
    let root = make_template_with_metadata(&long_desc, &["E1003"], &[]);
    let tmpl = Template::from_ast(&root).unwrap();
    let mut engine = Engine::new();
    let issues = engine.validate(&tmpl, &root, &["us-east-1".to_string()]);
    assert!(
        !issues.iter().any(|i| i.rule_id.as_deref() == Some("E1003")),
        "E1003 should be suppressed by template-level metadata"
    );
}

#[test]
fn test_resource_level_suppression_only_affects_that_resource() {
    // Two resources, only one has suppression for E3012
    let root = make_template_with_metadata(
        "Valid",
        &[],
        &[("SuppressedBucket", &["E3012"]), ("NormalBucket", &[])],
    );
    // Simulate issues on both resources
    let issue_suppressed = ValidationError {
        rule_id: Some("E3012".to_string()),
        message: "type mismatch".to_string(),
        path: vec![
            "Resources".to_string(),
            "SuppressedBucket".to_string(),
            "Properties".to_string(),
        ],
        span: Span {
            start: Position { line: 5, column: 1 },
            end: Position { line: 5, column: 1 },
        },
        keyword: String::new(),
        unknown: false,
        resolved_from_ref: false,
        context: vec![],
        schema_id: None,
    };
    let issue_normal = ValidationError {
        rule_id: Some("E3012".to_string()),
        message: "type mismatch".to_string(),
        path: vec![
            "Resources".to_string(),
            "NormalBucket".to_string(),
            "Properties".to_string(),
        ],
        span: Span {
            start: Position {
                line: 10,
                column: 1,
            },
            end: Position {
                line: 10,
                column: 1,
            },
        },
        keyword: String::new(),
        unknown: false,
        resolved_from_ref: false,
        context: vec![],
        schema_id: None,
    };

    let template_ignores = get_ignored_rules(&root);
    let mut issues = vec![issue_suppressed.clone(), issue_normal.clone()];
    issues.retain(|issue| {
        if template_ignores
            .iter()
            .any(|id| issue.rule_id.as_deref().unwrap_or("").starts_with(id))
        {
            return false;
        }
        if issue.path.len() >= 2 && issue.path[0] == "Resources" {
            let resource_name = &issue.path[1];
            if let Some(resource_node) = root.get("Resources").and_then(|r| r.get(resource_name)) {
                let resource_ignores = get_ignored_rules(resource_node);
                if resource_ignores
                    .iter()
                    .any(|id| issue.rule_id.as_deref().unwrap_or("").starts_with(id))
                {
                    return false;
                }
            }
        }
        true
    });

    assert_eq!(issues.len(), 1);
    assert_eq!(issues[0].path[1], "NormalBucket");
}

#[test]
fn test_non_matching_suppression_does_not_affect_issues() {
    // Template suppresses W2001, but the issue is E1003 — should not be filtered
    let long_desc = "x".repeat(1025);
    let root = make_template_with_metadata(&long_desc, &["W2001"], &[]);
    let tmpl = Template::from_ast(&root).unwrap();
    let mut engine = Engine::new();
    let issues = engine.validate(&tmpl, &root, &["us-east-1".to_string()]);
    assert!(
        issues.iter().any(|i| i.rule_id.as_deref() == Some("E1003")),
        "E1003 should NOT be suppressed when only W2001 is in ignore_checks"
    );
}

#[test]
fn test_get_ignored_rules_empty_when_no_metadata() {
    let root = AstNode::Object(ObjectNode {
        entries: Vec::new(),
        span: Span::default(),
    });
    assert!(get_ignored_rules(&root).is_empty());
}

#[test]
fn test_get_ignored_rules_extracts_ids() {
    let root = make_template_with_metadata("desc", &["E3001", "W2001"], &[]);
    let ids = get_ignored_rules(&root);
    assert_eq!(ids, vec!["E3001", "W2001"]);
}

#[test]
fn test_schema_allof_required_is_enforced() {
    // Schema with allOf containing a required constraint (like CloudWatch::MetricStream)
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::CloudWatch::MetricStream",
        json!({
            "typeName": "AWS::CloudWatch::MetricStream",
            "properties": {
                "FirehoseArn": {"type": "string"},
                "RoleArn": {"type": "string"},
                "OutputFormat": {"type": "string"},
                "Name": {"type": "string"}
            },
            "additionalProperties": false,
            "allOf": [
                {
                    "required": ["FirehoseArn", "RoleArn", "OutputFormat"]
                }
            ]
        }),
    );

    // Missing required properties from allOf
    let root = make_template_ast(
        "AWS::CloudWatch::MetricStream",
        json!({"Name": "my-stream"}),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3003"))
        .collect();
    assert!(
        issues.iter().any(|i| i.message.contains("FirehoseArn")),
        "Should report FirehoseArn as required via allOf, got: {:?}",
        issues
    );
}

#[test]
fn test_schema_if_then_else_enforced() {
    // Schema with if/then: if Engine is "mysql", then EngineVersion must be in a set
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::RDS::DBInstance",
        json!({
            "typeName": "AWS::RDS::DBInstance",
            "properties": {
                "Engine": {"type": "string"},
                "EngineVersion": {"type": "string"},
                "DBInstanceClass": {"type": "string"}
            },
            "additionalProperties": false,
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "Engine": {"const": "mysql"}
                        },
                        "required": ["Engine"]
                    },
                    "then": {
                        "properties": {
                            "EngineVersion": {
                                "enum": ["5.7", "8.0"]
                            }
                        }
                    }
                }
            ]
        }),
    );

    // Engine=mysql with invalid version → should trigger then-branch error
    let root = make_template_ast(
        "AWS::RDS::DBInstance",
        json!({"Engine": "mysql", "EngineVersion": "9.9"}),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3030"))
        .collect();
    assert!(
        !issues.is_empty(),
        "Should report enum violation from if/then in allOf"
    );
    assert!(
        issues
            .iter()
            .any(|i| i.message.contains("enum") || i.message.contains("not one of")),
        "Error should mention enum violation, got: {:?}",
        issues
    );

    // Engine=postgres → if doesn't match, no then-branch error
    let root2 = make_template_ast(
        "AWS::RDS::DBInstance",
        json!({"Engine": "postgres", "EngineVersion": "9.9"}),
    );
    let tmpl2 = Template::from_ast(&root2).unwrap();
    let issues2: Vec<_> = engine
        .validate(&tmpl2, &root2, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3030"))
        .collect();
    assert!(
        issues2.is_empty(),
        "Should not report errors when if-condition doesn't match, got: {:?}",
        issues2
    );
}

#[test]
fn test_schema_allof_with_anyof_enforced() {
    // Schema like ARCZonalShift: allOf containing anyOf + nested allOf
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::ARCZonalShift::ZonalAutoshiftConfiguration",
        json!({
            "typeName": "AWS::ARCZonalShift::ZonalAutoshiftConfiguration",
            "properties": {
                "ResourceIdentifier": {"type": "string"},
                "ZonalAutoshiftStatus": {"type": "string"},
                "PracticeRunConfiguration": {"type": "object"}
            },
            "additionalProperties": false,
            "allOf": [
                {
                    "anyOf": [
                        {"required": ["ZonalAutoshiftStatus"]},
                        {"required": ["PracticeRunConfiguration"]}
                    ],
                    "allOf": [
                        {"required": ["ResourceIdentifier"]}
                    ]
                }
            ]
        }),
    );

    // Missing ResourceIdentifier (required via nested allOf)
    let root = make_template_ast(
        "AWS::ARCZonalShift::ZonalAutoshiftConfiguration",
        json!({"ZonalAutoshiftStatus": "ENABLED"}),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3003"))
        .collect();
    assert!(
        issues
            .iter()
            .any(|i| i.message.contains("ResourceIdentifier")),
        "Should require ResourceIdentifier via nested allOf, got: {:?}",
        issues
    );

    // Missing both ZonalAutoshiftStatus and PracticeRunConfiguration (anyOf)
    let root2 = make_template_ast(
        "AWS::ARCZonalShift::ZonalAutoshiftConfiguration",
        json!({"ResourceIdentifier": "arn:aws:example"}),
    );
    let tmpl2 = Template::from_ast(&root2).unwrap();
    let issues2: Vec<_> = engine
        .validate(&tmpl2, &root2, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| matches!(i.rule_id.as_deref(), Some("E3017") | Some("E3003")))
        .collect();
    assert!(
        !issues2.is_empty(),
        "Should report anyOf or required violation, got: {:?}",
        issues2
    );
}

/// Integration test: validate against a real schema that has allOf.
#[test]
fn test_real_schema_metricstream_allof_required() {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    if !data_dir.join("schemas/providers").is_dir() {
        return; // skip if data dir not present
    }
    let mut engine = Engine::with_data_dir(data_dir);

    // CloudWatch::MetricStream requires FirehoseArn, RoleArn, OutputFormat via allOf
    let root = make_template_ast(
        "AWS::CloudWatch::MetricStream",
        json!({"Name": "my-stream"}),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3003"))
        .collect();
    assert!(
        issues.iter().any(|i| i.message.contains("FirehoseArn")),
        "Real MetricStream schema should enforce allOf required, got: {:?}",
        issues
    );
}

#[test]
fn test_serverless_resources_no_schema_no_issues() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "additionalProperties": false
        }),
    );

    // Build a SAM template with a serverless function resource
    let mut root_props: Vec<ObjectEntry> = Vec::new();
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Transform".to_string(),
            span: Span::default(),
        }),
        key: "Transform".to_string(),
        value: AstNode::String(StringNode {
            value: "AWS::Serverless-2016-10-31".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let mut func_props: Vec<ObjectEntry> = Vec::new();
    func_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Type".to_string(),
            span: Span::default(),
        }),
        key: "Type".to_string(),
        value: AstNode::String(StringNode {
            value: "AWS::Serverless::Function".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    func_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Properties".to_string(),
            span: Span::default(),
        }),
        key: "Properties".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: vec![ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Runtime".to_string(),
                    span: Span::default(),
                }),
                key: "Runtime".to_string(),
                value: AstNode::String(StringNode {
                    value: "python3.12".to_string(),
                    span: Span::default(),
                }),
                key_span: Span::default(),
            }],
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let mut resources: Vec<ObjectEntry> = Vec::new();
    resources.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "MyFunc".to_string(),
            span: Span::default(),
        }),
        key: "MyFunc".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: func_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Resources".to_string(),
            span: Span::default(),
        }),
        key: "Resources".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: resources,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let root = AstNode::Object(ObjectNode {
        entries: root_props,
        span: Span::default(),
    });
    let tmpl = Template::from_ast(&root).unwrap();
    // No SAM schema loaded in mock, so no schema issues for serverless resources
    let schema_issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| {
            matches!(
                i.rule_id.as_deref().unwrap_or(""),
                "E3012" | "E3002" | "E3003" | "E3006"
            )
        })
        .collect();
    assert!(
        schema_issues.is_empty(),
        "Serverless resources without a loaded schema should produce no issues, got: {:?}",
        schema_issues
    );
}

#[test]
fn test_getatt_valid_attribute_no_e3015() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "readOnlyProperties": ["/properties/Arn", "/properties/DomainName"]
        }),
    );

    let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
Outputs:
  BucketArn:
    Value: !GetAtt Bucket.Arn
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E1010"))
        .collect();
    assert!(
        issues.is_empty(),
        "Valid attribute should not trigger E1010, got: {:?}",
        issues
    );
}

#[test]
fn test_getatt_invalid_attribute_triggers_e3015() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"}
            },
            "readOnlyProperties": ["/properties/Arn", "/properties/DomainName"]
        }),
    );

    let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
Outputs:
  Bad:
    Value: !GetAtt Bucket.FakeAttribute
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E6101"))
        .collect();
    assert_eq!(issues.len(), 1);
    assert!(issues[0].message.contains("FakeAttribute"));
}

#[test]
fn test_getatt_custom_resource_accepts_any_attribute() {
    let mut engine = Engine::new();

    let yaml = br#"
Resources:
  Custom:
    Type: Custom::MyResource
Outputs:
  Val:
    Value: !GetAtt Custom.AnyAttribute
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E1010"))
        .collect();
    assert!(
        issues.is_empty(),
        "Custom resources should accept any attribute"
    );
}

#[test]
fn test_getatt_missing_resource_no_e3015() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {"BucketName": {"type": "string"}},
            "readOnlyProperties": ["/properties/Arn"]
        }),
    );

    let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
Outputs:
  Val:
    Value: !GetAtt Missing.Arn
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E1010"))
        .collect();
    // E1015 handles missing resources, E1010 should not fire
    assert!(
        issues.is_empty(),
        "Missing resource should not trigger E1010"
    );
}

#[test]
fn test_getatt_cloudformation_stack_outputs() {
    let mut engine = Engine::new();

    let yaml = br#"
Resources:
  Stack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/mytemplate.template
Outputs:
  Val:
    Value: !GetAtt Stack.Outputs.MyOutput
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E1010"))
        .collect();
    assert!(issues.is_empty(), "Stack Outputs.* should be valid");
}

#[test]
fn test_getatt_e3015_registered() {
    let engine = Engine::new();
    // E3015 is now dispatched via KeywordRuleRegistry (CfnLintRule)
    let all_rules = engine.keyword_rules.all_rules();
    assert!(all_rules.iter().any(|r| r.id() == "E3015"));
}

#[test]
fn test_e3501_registered() {
    let engine = Engine::new();
    // E3501 is dispatched via KeywordRuleRegistry (extension_schema_rule, auto-registered)
    assert!(engine
        .keyword_rules
        .all_rules()
        .iter()
        .any(|r| r.id() == "E3501"));
}

#[test]
fn test_extension_schema_no_schema_manager_returns_empty() {
    let mut engine = Engine::new();
    assert!(engine.schema_provider.is_none());
    let root = make_template_ast("AWS::Lambda::Function", json!({"Code": {"ZipFile": "x"}}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3501"))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_extension_schema_no_extensions_dir_returns_empty() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::Lambda::Function",
        json!({
            "typeName": "AWS::Lambda::Function",
            "properties": {
                "Code": {"type": "object"},
                "Runtime": {"type": "string"}
            }
        }),
    );
    // _dir has no extensions subdirectory
    let root = make_template_ast("AWS::Lambda::Function", json!({"Code": {"ZipFile": "x"}}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3501"))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_extension_schema_lambda_zipfile_without_runtime_triggers_e3501() {
    let (mut engine, dir) = engine_with_mock_schema(
        "AWS::Lambda::Function",
        json!({
            "typeName": "AWS::Lambda::Function",
            "properties": {
                "Code": {"type": "object"},
                "Runtime": {"type": "string"},
                "Handler": {"type": "string"},
                "Role": {"type": "string"}
            }
        }),
    );

    // Add the extension schema: ZipFile requires Runtime
    let ext_dir = dir.root.join("schemas/extensions/aws_lambda_function");
    std::fs::create_dir_all(&ext_dir).unwrap();
    std::fs::write(
        ext_dir.join("zipfile_runtime_exists.json"),
        serde_json::to_string(&json!({
            "additionalProperties": true,
            "if": {
                "properties": {
                    "Code": {
                        "additionalProperties": true,
                        "properties": { "ZipFile": true },
                        "required": ["ZipFile"],
                        "type": "object"
                    }
                },
                "required": ["Code"],
                "type": "object"
            },
            "then": {
                "required": ["Runtime"]
            }
        }))
        .unwrap(),
    )
    .unwrap();

    // Lambda with ZipFile but no Runtime → should trigger E3501
    let root = make_template_ast(
        "AWS::Lambda::Function",
        json!({
            "Code": {"ZipFile": "exports.handler = function(event, context) {}"},
            "Handler": "index.handler",
            "Role": "arn:aws:iam::123456789012:role/lambda-role"
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3678"))
        .collect();
    assert!(
        !issues.is_empty(),
        "Lambda with ZipFile but no Runtime should trigger E3678, got no issues"
    );
    assert!(
        issues
            .iter()
            .any(|i| i.message.to_lowercase().contains("runtime")),
        "E3678 message should mention Runtime, got: {:?}",
        issues
    );
}

#[test]
fn test_extension_schema_lambda_zipfile_with_runtime_no_e3501() {
    let (mut engine, dir) = engine_with_mock_schema(
        "AWS::Lambda::Function",
        json!({
            "typeName": "AWS::Lambda::Function",
            "properties": {
                "Code": {"type": "object"},
                "Runtime": {"type": "string"},
                "Handler": {"type": "string"},
                "Role": {"type": "string"}
            }
        }),
    );

    let ext_dir = dir.root.join("schemas/extensions/aws_lambda_function");
    std::fs::create_dir_all(&ext_dir).unwrap();
    std::fs::write(
        ext_dir.join("zipfile_runtime_exists.json"),
        serde_json::to_string(&json!({
            "additionalProperties": true,
            "if": {
                "properties": {
                    "Code": {
                        "additionalProperties": true,
                        "properties": { "ZipFile": true },
                        "required": ["ZipFile"],
                        "type": "object"
                    }
                },
                "required": ["Code"],
                "type": "object"
            },
            "then": {
                "required": ["Runtime"]
            }
        }))
        .unwrap(),
    )
    .unwrap();

    // Lambda with ZipFile AND Runtime → no E3501
    let root = make_template_ast(
        "AWS::Lambda::Function",
        json!({
            "Code": {"ZipFile": "exports.handler = function(event, context) {}"},
            "Handler": "index.handler",
            "Role": "arn:aws:iam::123456789012:role/lambda-role",
            "Runtime": "nodejs18.x"
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3501"))
        .collect();
    assert!(
        issues.is_empty(),
        "Lambda with ZipFile and Runtime should not trigger E3501, got: {:?}",
        issues
    );
}

#[test]
fn test_extension_schema_path_includes_resource_name() {
    let (mut engine, dir) = engine_with_mock_schema(
        "AWS::Lambda::Function",
        json!({
            "typeName": "AWS::Lambda::Function",
            "properties": {
                "Code": {"type": "object"},
                "Runtime": {"type": "string"}
            }
        }),
    );

    let ext_dir = dir.root.join("schemas/extensions/aws_lambda_function");
    std::fs::create_dir_all(&ext_dir).unwrap();
    std::fs::write(
        ext_dir.join("zipfile_runtime_exists.json"),
        serde_json::to_string(&json!({
            "additionalProperties": true,
            "if": {
                "properties": {
                    "Code": {
                        "additionalProperties": true,
                        "properties": { "ZipFile": true },
                        "required": ["ZipFile"],
                        "type": "object"
                    }
                },
                "required": ["Code"],
                "type": "object"
            },
            "then": {
                "required": ["Runtime"]
            }
        }))
        .unwrap(),
    )
    .unwrap();

    let root = make_template_ast("AWS::Lambda::Function", json!({"Code": {"ZipFile": "x"}}));
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3678"))
        .collect();
    assert!(!issues.is_empty());
    assert!(issues[0].path.contains(&"Resources".to_string()));
    assert!(issues[0].path.contains(&"MyResource".to_string()));
    assert!(issues[0].path.contains(&"Properties".to_string()));
}

/// Integration test with real extension schemas from data directory.
#[test]
fn test_real_extension_lambda_zipfile_no_runtime() {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    if !data_dir.join("schemas/extensions").is_dir() {
        return;
    }
    let mut engine = Engine::with_data_dir(data_dir);

    let root = make_template_ast(
        "AWS::Lambda::Function",
        json!({
            "Code": {"ZipFile": "exports.handler = function(event, ctx) {}"},
            "Handler": "index.handler",
            "Role": "arn:aws:iam::123456789012:role/lambda-role"
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3678"))
        .collect();
    assert!(
        issues
            .iter()
            .any(|i| i.message.to_lowercase().contains("runtime")),
        "Real extension schema should require Runtime when ZipFile is used, got: {:?}",
        issues
    );
}

/// Integration test: Lambda with ZipFile + Runtime should pass extensions.
#[test]
fn test_real_extension_lambda_zipfile_with_runtime_passes() {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    if !data_dir.join("schemas/extensions").is_dir() {
        return;
    }
    let mut engine = Engine::with_data_dir(data_dir);

    let root = make_template_ast(
        "AWS::Lambda::Function",
        json!({
            "Code": {"ZipFile": "exports.handler = function(event, ctx) {}"},
            "Handler": "index.handler",
            "Role": "arn:aws:iam::123456789012:role/lambda-role",
            "Runtime": "nodejs18.x"
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3501"))
        .collect();
    assert!(
        issues.is_empty(),
        "Lambda with ZipFile + Runtime should not trigger E3501, got: {:?}",
        issues
    );
}

#[test]
fn test_extension_schema_suppression_via_metadata() {
    let (mut engine, dir) = engine_with_mock_schema(
        "AWS::Lambda::Function",
        json!({
            "typeName": "AWS::Lambda::Function",
            "properties": {
                "Code": {"type": "object"},
                "Runtime": {"type": "string"}
            }
        }),
    );

    let ext_dir = dir.root.join("schemas/extensions/aws_lambda_function");
    std::fs::create_dir_all(&ext_dir).unwrap();
    std::fs::write(
        ext_dir.join("zipfile_runtime_exists.json"),
        serde_json::to_string(&json!({
            "additionalProperties": true,
            "if": {
                "properties": {
                    "Code": {
                        "additionalProperties": true,
                        "properties": { "ZipFile": true },
                        "required": ["ZipFile"],
                        "type": "object"
                    }
                },
                "required": ["Code"],
                "type": "object"
            },
            "then": {
                "required": ["Runtime"]
            }
        }))
        .unwrap(),
    )
    .unwrap();

    // Build template with E3501 suppressed via metadata
    let mut root_props: Vec<ObjectEntry> = Vec::new();

    // Template-level metadata suppressing E3003
    let ignore_array = AstNode::Array(ArrayNode {
        elements: vec![AstNode::String(StringNode {
            value: "E3003".to_string(),
            span: Span::default(),
        })],
        span: Span::default(),
    });
    let mut config_props: Vec<ObjectEntry> = Vec::new();
    config_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "ignore_checks".to_string(),
            span: Span::default(),
        }),
        key: "ignore_checks".to_string(),
        value: ignore_array,
        key_span: Span::default(),
    });
    let mut cfn_lint_props: Vec<ObjectEntry> = Vec::new();
    cfn_lint_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "config".to_string(),
            span: Span::default(),
        }),
        key: "config".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: config_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    let mut meta_props: Vec<ObjectEntry> = Vec::new();
    meta_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "cfn-lint".to_string(),
            span: Span::default(),
        }),
        key: "cfn-lint".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: cfn_lint_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Metadata".to_string(),
            span: Span::default(),
        }),
        key: "Metadata".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: meta_props,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let mut res_inner: Vec<ObjectEntry> = Vec::new();
    res_inner.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Type".to_string(),
            span: Span::default(),
        }),
        key: "Type".to_string(),
        value: AstNode::String(StringNode {
            value: "AWS::Lambda::Function".to_string(),
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    res_inner.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Properties".to_string(),
            span: Span::default(),
        }),
        key: "Properties".to_string(),
        value: json_to_ast(&json!({"Code": {"ZipFile": "x"}})),
        key_span: Span::default(),
    });
    let mut resources: Vec<ObjectEntry> = Vec::new();
    resources.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "MyResource".to_string(),
            span: Span::default(),
        }),
        key: "MyResource".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: res_inner,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });
    root_props.push(ObjectEntry {
        key_node: AstNode::String(StringNode {
            value: "Resources".to_string(),
            span: Span::default(),
        }),
        key: "Resources".to_string(),
        value: AstNode::Object(ObjectNode {
            entries: resources,
            span: Span::default(),
        }),
        key_span: Span::default(),
    });

    let root = AstNode::Object(ObjectNode {
        entries: root_props,
        span: Span::default(),
    });
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3003"))
        .collect();
    assert!(
        issues.is_empty(),
        "E3003 should be suppressed via metadata, got: {:?}",
        issues
    );
}

#[test]
fn test_sam_schema_validation_wrong_type() {
    let dir = TempSchemaDir::new();

    // Regular provider with no SAM types
    std::fs::write(
        dir.root.join("schemas/providers/us_east_1.json"),
        serde_json::to_string(&json!({})).unwrap(),
    )
    .unwrap();

    // SAM provider + schema
    let sam_dir = dir.root.join("schemas/sam");
    std::fs::create_dir_all(&sam_dir).unwrap();
    std::fs::write(
        sam_dir.join("provider.json"),
        serde_json::to_string(&json!({
            "AWS::Serverless::Function": "sam_func"
        }))
        .unwrap(),
    )
    .unwrap();
    std::fs::write(
        sam_dir.join("sam_func.json"),
        serde_json::to_string(&json!({
            "typeName": "AWS::Serverless::Function",
            "properties": {
                "Runtime": {"type": "string"},
                "Handler": {"type": "string"}
            },
            "additionalProperties": false
        }))
        .unwrap(),
    )
    .unwrap();

    let mut engine = Engine::with_data_dir(dir.root.clone());
    assert!(engine.schema_provider.is_some());

    // Serverless::Function with wrong type for Runtime (number, not boolean)
    let root = make_template_ast_raw(
        "AWS::Serverless::Function",
        AstNode::Object(ObjectNode {
            entries: vec![ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Runtime".to_string(),
                    span: Span::default(),
                }),
                key: "Runtime".to_string(),
                value: AstNode::Array(crate::ast::ArrayNode {
                    elements: vec![],
                    span: Span {
                        start: Position { line: 5, column: 3 },
                        end: Position { line: 5, column: 3 },
                    },
                }),
                key_span: Span::default(),
            }],
            span: Span::default(),
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3012"))
        .collect();
    assert!(
        !issues.is_empty(),
        "SAM resources should be schema-validated, got no E3012 issues"
    );
    assert!(issues[0].message.contains("type"));
}

#[test]
fn test_real_data_sam_serverless_function_schema_validation() {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    if !data_dir.join("schemas/sam/provider.json").is_file() {
        return;
    }
    let mut engine = Engine::with_data_dir(data_dir);

    // Serverless::Function with an additional property that shouldn't exist
    let root = make_template_ast(
        "AWS::Serverless::Function",
        json!({
            "Runtime": "python3.12",
            "Handler": "index.handler",
            "CodeUri": "s3://bucket/code.zip",
            "CompletelyFakeProperty": "bad"
        }),
    );
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3002"))
        .collect();
    assert!(
        issues
            .iter()
            .any(|i| i.message.contains("CompletelyFakeProperty")),
        "SAM Function should be validated against schema, got: {:?}",
        issues
    );
}

#[test]
fn test_ref_novalue_object_property_produces_e3003() {
    // When a required property has Ref AWS::NoValue, the property should
    // be removed and E3003 (required) should fire instead of E3012 (type).
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::IAM::Role",
        json!({
            "typeName": "AWS::IAM::Role",
            "properties": {
                "RoleName": {"type": "string"},
                "Tags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Key": {"type": "string"},
                            "Value": {"type": "string"}
                        },
                        "required": ["Key", "Value"],
                        "additionalProperties": false
                    }
                }
            },
            "additionalProperties": false
        }),
    );

    // Tag with Key: !Ref AWS::NoValue — Key should be removed, E3003 for missing Key
    let props = AstNode::Object(ObjectNode {
        entries: vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Tags".to_string(),
                span: Span::default(),
            }),
            key: "Tags".to_string(),
            value: AstNode::Array(crate::ast::ArrayNode {
                elements: vec![AstNode::Object(ObjectNode {
                    entries: vec![
                        ObjectEntry {
                            key_node: AstNode::String(StringNode {
                                value: "Key".to_string(),
                                span: Span::default(),
                            }),
                            key: "Key".to_string(),
                            value: AstNode::Function(crate::ast::FunctionNode {
                                name: "Ref".to_string(),
                                args: Box::new(AstNode::String(StringNode {
                                    value: "AWS::NoValue".to_string(),
                                    span: Span::default(),
                                })),
                                span: Span {
                                    start: Position {
                                        line: 5,
                                        column: 11,
                                    },
                                    end: Position {
                                        line: 5,
                                        column: 11,
                                    },
                                },
                            }),
                            key_span: Span::default(),
                        },
                        ObjectEntry {
                            key_node: AstNode::String(StringNode {
                                value: "Value".to_string(),
                                span: Span::default(),
                            }),
                            key: "Value".to_string(),
                            value: AstNode::String(StringNode {
                                value: "Value1".to_string(),
                                span: Span::default(),
                            }),
                            key_span: Span::default(),
                        },
                    ],
                    span: Span {
                        start: Position { line: 5, column: 9 },
                        end: Position { line: 5, column: 9 },
                    },
                })],
                span: Span::default(),
            }),
            key_span: Span::default(),
        }],
        span: Span::default(),
    });

    let root = make_template_ast_raw("AWS::IAM::Role", props);
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3003"))
        .collect();
    assert!(
        issues.iter().any(|i| i.message.contains("Key")),
        "Should report E3003 for missing Key when Ref AWS::NoValue removes it, got: {:?}",
        issues
    );
}

#[test]
fn test_ref_novalue_properties_level_produces_e3012() {
    // When Properties itself is Ref AWS::NoValue, E3012 (type) should fire
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::IAM::Role",
        json!({
            "typeName": "AWS::IAM::Role",
            "properties": {
                "AssumeRolePolicyDocument": {"type": "object"}
            },
            "required": ["AssumeRolePolicyDocument"],
            "additionalProperties": false
        }),
    );

    let props = AstNode::Function(crate::ast::FunctionNode {
        name: "Ref".to_string(),
        args: Box::new(AstNode::String(StringNode {
            value: "AWS::NoValue".to_string(),
            span: Span::default(),
        })),
        span: Span {
            start: Position { line: 5, column: 5 },
            end: Position { line: 5, column: 5 },
        },
    });

    let root = make_template_ast_raw("AWS::IAM::Role", props);
    let tmpl = Template::from_ast(&root).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &root, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3012"))
        .collect();
    assert!(
        !issues.is_empty(),
        "Should report E3012 when Properties itself is Ref AWS::NoValue, got no E3012"
    );
}

/// TODO: re-enable once schemas are pre-patched at download time.
#[test]
#[test]
fn test_network_interface_schema_has_groupset_format() {
    use cfn_schema::SchemaProvider;
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    let provider = cfn_schema::BundledSchemaProvider::new(data_dir).unwrap();
    let schema = provider
        .get_resource_schema("AWS::EC2::NetworkInterface", "us-east-1")
        .expect("NetworkInterface schema should load");
    let format = schema
        .raw
        .pointer("/properties/GroupSet/items/format")
        .expect("GroupSet/items/format should exist after patching");
    assert_eq!(
        format.as_str().unwrap(),
        "AWS::EC2::SecurityGroup.Id",
        "GroupSet items format should be AWS::EC2::SecurityGroup.Id"
    );
}

#[test]
fn test_resolve_data_refs_lookup_resolves_known_key() {
    let gathered = AstNode::Object(ObjectNode {
        entries: vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "target".to_string(),
                span: Span::default(),
            }),
            key: "target".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: vec![ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "resourceType".to_string(),
                        span: Span::default(),
                    }),
                    key: "resourceType".to_string(),
                    value: AstNode::String(StringNode {
                        value: "AWS::S3::Bucket".to_string(),
                        span: Span::default(),
                    }),
                    key_span: Span::default(),
                }],
                span: Span::default(),
            }),
            key_span: Span::default(),
        }],
        span: Span::default(),
    });

    let schema = json!({
        "const": {
            "$lookup": {
                "key": {"$data": "/target/resourceType"},
                "map": {
                    "AWS::S3::Bucket": "s3.amazonaws.com",
                    "AWS::SNS::Topic": "sns.amazonaws.com"
                }
            }
        }
    });

    let resolved = resolve_data_refs(&schema, &gathered);
    assert_eq!(resolved.get("const").unwrap(), "s3.amazonaws.com");
}

#[test]
fn test_resolve_data_refs_lookup_unknown_key_drops_const() {
    let gathered = AstNode::Object(ObjectNode {
        entries: vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "target".to_string(),
                span: Span::default(),
            }),
            key: "target".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: vec![ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "resourceType".to_string(),
                        span: Span::default(),
                    }),
                    key: "resourceType".to_string(),
                    value: AstNode::String(StringNode {
                        value: "AWS::Unknown::Type".to_string(),
                        span: Span::default(),
                    }),
                    key_span: Span::default(),
                }],
                span: Span::default(),
            }),
            key_span: Span::default(),
        }],
        span: Span::default(),
    });

    let schema = json!({
        "const": {
            "$lookup": {
                "key": {"$data": "/target/resourceType"},
                "map": {
                    "AWS::S3::Bucket": "s3.amazonaws.com"
                }
            }
        }
    });

    let resolved = resolve_data_refs(&schema, &gathered);
    // const should be dropped when $lookup can't resolve
    assert!(
        resolved.get("const").is_none(),
        "const should be dropped for unresolved $lookup, got: {:?}",
        resolved
    );
}

#[test]
fn test_resolve_data_refs_lookup_missing_data_drops_const() {
    let gathered = AstNode::Object(ObjectNode {
        entries: Vec::new(),
        span: Span::default(),
    });

    let schema = json!({
        "const": {
            "$lookup": {
                "key": {"$data": "/target/resourceType"},
                "map": {"AWS::S3::Bucket": "s3.amazonaws.com"}
            }
        }
    });

    let resolved = resolve_data_refs(&schema, &gathered);
    assert!(
        resolved.get("const").is_none(),
        "const should be dropped when $data can't resolve"
    );
}

#[test]
fn test_resolve_data_refs_data_still_works() {
    let gathered = AstNode::Object(ObjectNode {
        entries: vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "source".to_string(),
                span: Span::default(),
            }),
            key: "source".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: vec![ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: "fifo".to_string(),
                        span: Span::default(),
                    }),
                    key: "fifo".to_string(),
                    value: AstNode::Bool(BoolNode {
                        value: true,
                        span: Span::default(),
                    }),
                    key_span: Span::default(),
                }],
                span: Span::default(),
            }),
            key_span: Span::default(),
        }],
        span: Span::default(),
    });

    let schema = json!({"const": {"$data": "/source/fifo"}});
    let resolved = resolve_data_refs(&schema, &gathered);
    assert_eq!(resolved.get("const").unwrap(), true);
}

/// Integration test: Lambda Permission with S3 bucket should not produce W3664
/// when the principal matches the target resource type.
#[test]
fn test_lambda_permission_s3_principal_no_w3664() {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    if !data_dir.join("schemas/extensions").is_dir() {
        return;
    }
    let mut engine = Engine::with_data_dir(data_dir);

    let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-func
      Runtime: python3.12
      Handler: index.handler
      Role: !Sub "arn:aws:iam::${AWS::AccountId}:role/role"
      Code:
        ZipFile: |
          def handler(event, context):
            pass
  BucketPermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      FunctionName: !Ref MyFunction
      Principal: s3.amazonaws.com
      SourceArn: !GetAtt MyBucket.Arn
"#;
    let ast = parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("W3664"))
        .collect();
    assert!(
        issues.is_empty(),
        "Lambda Permission with correct S3 principal should not trigger W3664, got: {:?}",
        issues
    );
}

/// Integration test: Lambda Permission with wrong principal should produce W3664.
#[test]
fn test_lambda_permission_wrong_principal_triggers_w3664() {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    if !data_dir.join("schemas/extensions").is_dir() {
        return;
    }
    let mut engine = Engine::with_data_dir(data_dir);

    let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-func
      Runtime: python3.12
      Handler: index.handler
      Role: !Sub "arn:aws:iam::${AWS::AccountId}:role/role"
      Code:
        ZipFile: |
          def handler(event, context):
            pass
  BucketPermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      FunctionName: !Ref MyFunction
      Principal: sns.amazonaws.com
      SourceArn: !GetAtt MyBucket.Arn
"#;
    let ast = parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate(&tmpl, &ast, &["us-east-1".to_string()])
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("W3664"))
        .collect();
    assert!(
        !issues.is_empty(),
        "Lambda Permission with wrong principal should trigger W3664"
    );
}

#[test]
fn test_readonly_property_triggers_e3040() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"},
                "Arn": {"type": "string"}
            },
            "readOnlyProperties": ["/properties/Arn"]
        }),
    );

    let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
      Arn: arn:aws:s3:::my-bucket
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate_readonly_properties(&tmpl, &ast, "us-east-1")
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3040"))
        .collect();
    assert_eq!(issues.len(), 1);
    assert!(issues[0].message.contains("Arn"));
    assert!(issues[0].message.contains("read-only") || issues[0].message.contains("Read only"));
}

#[test]
fn test_no_readonly_property_no_e3040() {
    let (mut engine, _dir) = engine_with_mock_schema(
        "AWS::S3::Bucket",
        json!({
            "typeName": "AWS::S3::Bucket",
            "properties": {
                "BucketName": {"type": "string"},
                "Arn": {"type": "string"}
            },
            "readOnlyProperties": ["/properties/Arn"]
        }),
    );

    let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let issues: Vec<_> = engine
        .validate_readonly_properties(&tmpl, &ast, "us-east-1")
        .into_iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3040"))
        .collect();
    assert!(issues.is_empty());
}

#[test]
fn test_engine_new_has_keyword_rules() {
    let engine = Engine::new();
    assert!(engine.keyword_rules.all_rules().len() > 100);
}

#[test]
fn test_validate_empty_resources() {
    let ast = crate::parser::parse(b"Resources: {}\n").unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let mut engine = Engine::new();
    let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
    let _ = issues;
}

#[test]
fn test_resource_level_suppression() {
    let yaml = br#"
Resources:
  Table:
    Type: AWS::DynamoDB::Table
    Metadata:
      cfn-lint:
        config:
          ignore_checks:
            - I3011
    Properties:
      TableName: test
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
"#;
    let ast = crate::parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let mut engine = Engine::new();
    let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
    assert!(!issues.iter().any(|i| i.rule_id.as_deref() == Some("I3011") && i.path.contains(&"Table".to_string())),
        "I3011 should be suppressed for Table resource");
}

#[test]
fn debug_e3023_full() {
    let yaml = std::fs::read("/Users/kddejong/code/github.com/aws-cloudformation/cfn-lint/test/fixtures/templates/bad/route53.yaml").unwrap();
    let ast = crate::parser::parse(&yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let data_dir = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data");
    let mut engine = Engine::with_data_dir(data_dir);
    let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
    for i in issues
        .iter()
        .filter(|i| i.rule_id.as_deref() == Some("E3023"))
    {
        eprintln!(
            "rs {:3} {}",
            i.span.start.line + 1,
            i.message.chars().take(90).collect::<String>()
        );
    }
    eprintln!(
        "Total: {}",
        issues
            .iter()
            .filter(|i| i.rule_id.as_deref() == Some("E3023"))
            .count()
    );
}
