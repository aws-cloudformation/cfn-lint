//! SAM Globals merging for pre-validation processing.
//!
//! Merges properties from the `Globals` section into matching SAM resources
//! **before** validation runs. This ensures that schema validation and rules
//! see globally-set properties on each resource.
//!
//! Merge semantics match the SAM translator / cfn-lint v1:
//! - Primitives/intrinsics: local value wins
//! - Dict + dict: recursive merge, local keys override; BUT if either side is
//!   an intrinsic function (Ref, Fn::*), local wins wholesale
//! - List + list: concatenate global + local
//! - Type mismatch: local wins
//!
//! The `IgnoreGlobals` attribute is honored:
//! - `IgnoreGlobals: "*"` — skip the resource entirely
//! - `IgnoreGlobals: [keys]` — drop those keys from globals before merging

use std::collections::HashMap;

use crate::ast::{ArrayNode, AstNode, ObjectEntry, ObjectNode, Span, StringNode};

/// Globals section key → resource type mapping.
static GLOBALS_TYPE_MAP: &[(&str, &str)] = &[
    ("Function", "AWS::Serverless::Function"),
    ("Api", "AWS::Serverless::Api"),
    ("HttpApi", "AWS::Serverless::HttpApi"),
    ("SimpleTable", "AWS::Serverless::SimpleTable"),
    ("StateMachine", "AWS::Serverless::StateMachine"),
    ("LayerVersion", "AWS::Serverless::LayerVersion"),
    ("CapacityProvider", "AWS::Serverless::CapacityProvider"),
    ("WebSocketApi", "AWS::Serverless::WebSocketApi"),
];

/// Check if a node is an intrinsic function (Ref or Fn::*).
fn is_intrinsic(node: &AstNode) -> bool {
    matches!(node, AstNode::Function(_))
}

/// Merge a global value with a local value, preserving spans where possible.
///
/// Rules (matching SAM translator behavior):
/// - Primitives/intrinsics: local wins
/// - Dicts: recursive merge, local keys override; BUT if either side is an
///   intrinsic function, local wins wholesale
/// - Lists: concatenate global + local
/// - Type mismatch: local wins
fn merge_values(global: &AstNode, local: &AstNode) -> AstNode {
    // If either is an intrinsic, local wins
    if is_intrinsic(global) || is_intrinsic(local) {
        return local.clone();
    }

    match (global, local) {
        // Dict + Dict: recursive merge
        (AstNode::Object(g_obj), AstNode::Object(l_obj)) => {
            let mut merged_entries: Vec<ObjectEntry> = Vec::new();

            // Start with global entries, merging where local has the same key
            for g_entry in &g_obj.entries {
                if let Some(l_entry) = l_obj.entries.iter().find(|e| e.key == g_entry.key) {
                    // Both have this key: merge recursively
                    merged_entries.push(ObjectEntry {
                        key_node: l_entry.key_node.clone(),
                        key: l_entry.key.clone(),
                        value: merge_values(&g_entry.value, &l_entry.value),
                        key_span: l_entry.key_span,
                    });
                } else {
                    // Only global has this key
                    merged_entries.push(g_entry.clone());
                }
            }

            // Add local-only entries
            for l_entry in &l_obj.entries {
                if !g_obj.entries.iter().any(|e| e.key == l_entry.key) {
                    merged_entries.push(l_entry.clone());
                }
            }

            AstNode::Object(ObjectNode {
                entries: merged_entries,
                // Use local span as primary (most relevant for error reporting)
                span: l_obj.span,
            })
        }

        // List + List: concatenate global + local
        (AstNode::Array(g_arr), AstNode::Array(l_arr)) => {
            let mut elements = g_arr.elements.clone();
            elements.extend(l_arr.elements.iter().cloned());
            AstNode::Array(ArrayNode {
                elements,
                // Use local span
                span: l_arr.span,
            })
        }

        // Type mismatch or primitives: local wins
        _ => local.clone(),
    }
}

/// Build a map of resource_type → global properties from the Globals section.
fn build_globals_map(globals_node: &AstNode) -> HashMap<&'static str, AstNode> {
    let mut map = HashMap::new();

    let obj = match globals_node.as_object() {
        Some(o) => o,
        None => return map,
    };

    for (section_name, props) in obj.iter() {
        // Find the resource type for this globals section
        if let Some((_, resource_type)) = GLOBALS_TYPE_MAP
            .iter()
            .find(|(key, _)| *key == section_name)
        {
            if props.as_object().is_some() {
                map.insert(*resource_type, props.clone());
            }
        }
    }

    map
}

/// Get the IgnoreGlobals value from a resource node.
fn get_ignore_globals(resource_node: &AstNode) -> Option<IgnoreGlobals> {
    let obj = resource_node.as_object()?;
    let ignore = obj.get("IgnoreGlobals")?;

    match ignore {
        AstNode::String(s) if s.value == "*" => Some(IgnoreGlobals::All),
        AstNode::Array(arr) => {
            let keys: Vec<String> = arr
                .elements
                .iter()
                .filter_map(|e| e.as_str().map(String::from))
                .collect();
            if keys.is_empty() {
                None
            } else {
                Some(IgnoreGlobals::Keys(keys))
            }
        }
        _ => None,
    }
}

enum IgnoreGlobals {
    All,
    Keys(Vec<String>),
}

/// Apply IgnoreGlobals filtering to global properties.
fn filter_global_props(global_props: &AstNode, ignore: &IgnoreGlobals) -> Option<AstNode> {
    match ignore {
        IgnoreGlobals::All => None,
        IgnoreGlobals::Keys(keys) => {
            let obj = global_props.as_object()?;
            let filtered_entries: Vec<ObjectEntry> = obj
                .entries
                .iter()
                .filter(|e| !keys.contains(&e.key))
                .cloned()
                .collect();

            if filtered_entries.is_empty() {
                None
            } else {
                Some(AstNode::Object(ObjectNode {
                    entries: filtered_entries,
                    span: obj.span,
                }))
            }
        }
    }
}

/// Merge Globals properties into SAM resources in the AST.
///
/// Returns a new AST with merged properties. The original AST is not modified.
/// Does nothing if there is no Globals section or if the template is not a SAM template.
///
/// This should be called **before** validation runs.
pub fn merge_globals(root: &AstNode) -> AstNode {
    // Check if this is a SAM template
    if !crate::transform::is_sam_template(root) {
        return root.clone();
    }

    let root_obj = match root.as_object() {
        Some(o) => o,
        None => return root.clone(),
    };

    // Get Globals section
    let globals_node = match root_obj.get("Globals") {
        Some(g) => g,
        None => return root.clone(),
    };

    // Build map of resource_type → global properties
    let globals_map = build_globals_map(globals_node);
    if globals_map.is_empty() {
        return root.clone();
    }

    // Get Resources section
    let resources_node = match root_obj.get("Resources") {
        Some(r) => r,
        None => return root.clone(),
    };

    let resources_obj = match resources_node.as_object() {
        Some(o) => o,
        None => return root.clone(),
    };

    // Build new Resources section with merged properties
    let mut new_resource_entries: Vec<ObjectEntry> = Vec::new();

    for entry in &resources_obj.entries {
        let resource_node = &entry.value;

        // Get resource type
        let resource_type = match resource_node
            .as_object()
            .and_then(|o| o.get("Type"))
            .and_then(|t| t.as_str())
        {
            Some(t) => t,
            None => {
                // No Type field, keep as-is
                new_resource_entries.push(entry.clone());
                continue;
            }
        };

        // Check if we have globals for this resource type
        let global_props = match globals_map.get(resource_type) {
            Some(g) => g,
            None => {
                // No globals for this type
                new_resource_entries.push(entry.clone());
                continue;
            }
        };

        // Check IgnoreGlobals
        let effective_globals = match get_ignore_globals(resource_node) {
            Some(IgnoreGlobals::All) => {
                // Skip this resource entirely
                new_resource_entries.push(entry.clone());
                continue;
            }
            Some(ref ignore @ IgnoreGlobals::Keys(_)) => {
                match filter_global_props(global_props, ignore) {
                    Some(filtered) => filtered,
                    None => {
                        // All global keys filtered out
                        new_resource_entries.push(entry.clone());
                        continue;
                    }
                }
            }
            None => global_props.clone(),
        };

        // Merge properties
        let resource_obj = resource_node.as_object().unwrap(); // Safe: checked above
        let local_props = resource_obj.get("Properties");

        let merged_props = match local_props {
            Some(local) => merge_values(&effective_globals, local),
            None => {
                // No local Properties: use globals as-is (wrapped in Properties)
                effective_globals.clone()
            }
        };

        // Build new resource node with merged Properties
        let mut new_resource_entries_inner: Vec<ObjectEntry> = Vec::new();
        let mut found_properties = false;

        for res_entry in &resource_obj.entries {
            if res_entry.key == "Properties" {
                found_properties = true;
                new_resource_entries_inner.push(ObjectEntry {
                    key_node: res_entry.key_node.clone(),
                    key: res_entry.key.clone(),
                    value: merged_props.clone(),
                    key_span: res_entry.key_span,
                });
            } else {
                new_resource_entries_inner.push(res_entry.clone());
            }
        }

        // If resource had no Properties key, add one
        if !found_properties {
            new_resource_entries_inner.push(ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Properties".to_string(),
                    span: Span::default(),
                }),
                key: "Properties".to_string(),
                value: merged_props,
                key_span: Span::default(),
            });
        }

        let new_resource_node = AstNode::Object(ObjectNode {
            entries: new_resource_entries_inner,
            span: resource_obj.span,
        });

        new_resource_entries.push(ObjectEntry {
            key_node: entry.key_node.clone(),
            key: entry.key.clone(),
            value: new_resource_node,
            key_span: entry.key_span,
        });
    }

    // Build new root with updated Resources
    let new_resources = AstNode::Object(ObjectNode {
        entries: new_resource_entries,
        span: resources_obj.span,
    });

    let mut new_root_entries: Vec<ObjectEntry> = Vec::new();
    for entry in &root_obj.entries {
        if entry.key == "Resources" {
            new_root_entries.push(ObjectEntry {
                key_node: entry.key_node.clone(),
                key: entry.key.clone(),
                value: new_resources.clone(),
                key_span: entry.key_span,
            });
        } else {
            new_root_entries.push(entry.clone());
        }
    }

    AstNode::Object(ObjectNode {
        entries: new_root_entries,
        span: root_obj.span,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    fn parse_yaml(yaml: &[u8]) -> AstNode {
        parser::parse(yaml).unwrap()
    }

    fn get_resource_prop<'a>(root: &'a AstNode, resource: &str, prop: &str) -> Option<&'a AstNode> {
        root.get("Resources")?
            .get(resource)?
            .get("Properties")?
            .get(prop)
    }

    #[test]
    fn test_merge_primitive_local_wins() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 60
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Local Timeout (60) should win over global (30)
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(60.0));

        // Global Runtime should be inherited
        let runtime = get_resource_prop(&merged, "MyFunction", "Runtime").unwrap();
        assert_eq!(runtime.as_str(), Some("python3.9"));
    }

    #[test]
    fn test_merge_dict_recursive() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Environment:
      Variables:
        LOG_LEVEL: DEBUG
        APP_NAME: global
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          APP_NAME: local
          OTHER_VAR: value
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        let env = get_resource_prop(&merged, "MyFunction", "Environment").unwrap();
        let vars = env.get("Variables").unwrap();

        // LOG_LEVEL from global
        assert_eq!(vars.get("LOG_LEVEL").unwrap().as_str(), Some("DEBUG"));
        // APP_NAME local wins
        assert_eq!(vars.get("APP_NAME").unwrap().as_str(), Some("local"));
        // OTHER_VAR from local
        assert_eq!(vars.get("OTHER_VAR").unwrap().as_str(), Some("value"));
    }

    #[test]
    fn test_merge_list_concat() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Layers:
      - arn:aws:lambda:us-east-1:123456789012:layer:global-layer:1
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Layers:
        - arn:aws:lambda:us-east-1:123456789012:layer:local-layer:1
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        let layers = get_resource_prop(&merged, "MyFunction", "Layers")
            .unwrap()
            .as_array()
            .unwrap();

        // Should have global layer first, then local
        assert_eq!(layers.elements.len(), 2);
        assert!(layers.elements[0]
            .as_str()
            .unwrap()
            .contains("global-layer"));
        assert!(layers.elements[1].as_str().unwrap().contains("local-layer"));
    }

    #[test]
    fn test_merge_intrinsic_local_wins() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Environment:
      Variables:
        LOG_LEVEL: DEBUG
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment: !Ref MyEnvVar
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Local intrinsic should win over global dict
        let env = get_resource_prop(&merged, "MyFunction", "Environment").unwrap();
        assert!(env.as_function().is_some());
        let func = env.as_function().unwrap();
        assert_eq!(func.name, "Ref");
    }

    #[test]
    fn test_merge_global_intrinsic_local_wins() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Environment: !Ref GlobalEnvVar
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Environment:
        Variables:
          KEY: value
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Local dict should win over global intrinsic
        let env = get_resource_prop(&merged, "MyFunction", "Environment").unwrap();
        assert!(env.as_object().is_some());
        let vars = env.get("Variables").unwrap();
        assert_eq!(vars.get("KEY").unwrap().as_str(), Some("value"));
    }

    #[test]
    fn test_ignore_globals_star() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals: "*"
    Properties:
      Timeout: 60
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Should only have local Timeout, no Runtime
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(60.0));

        let runtime = get_resource_prop(&merged, "MyFunction", "Runtime");
        assert!(runtime.is_none());
    }

    #[test]
    fn test_ignore_globals_keys() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
    MemorySize: 256
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Timeout
      - MemorySize
    Properties:
      Handler: index.handler
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Should have Runtime from globals (not ignored)
        let runtime = get_resource_prop(&merged, "MyFunction", "Runtime").unwrap();
        assert_eq!(runtime.as_str(), Some("python3.9"));

        // Should have Handler from local
        let handler = get_resource_prop(&merged, "MyFunction", "Handler").unwrap();
        assert_eq!(handler.as_str(), Some("index.handler"));

        // Should NOT have Timeout or MemorySize from globals (ignored)
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout");
        assert!(timeout.is_none());

        let memory = get_resource_prop(&merged, "MyFunction", "MemorySize");
        assert!(memory.is_none());
    }

    #[test]
    fn test_no_globals_section() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 60
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Should be unchanged
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(60.0));
    }

    #[test]
    fn test_not_sam_template() {
        let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Globals:
  Function:
    Timeout: 30
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Should be unchanged (not a SAM template)
        let globals = merged.get("Globals");
        assert!(globals.is_some());
    }

    #[test]
    fn test_resource_without_properties() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Should have Properties added with globals
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(30.0));

        let runtime = get_resource_prop(&merged, "MyFunction", "Runtime").unwrap();
        assert_eq!(runtime.as_str(), Some("python3.9"));
    }

    #[test]
    fn test_multiple_resource_types() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
  Api:
    StageName: prod
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: MyApi
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Function should get Timeout from globals
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(30.0));

        // Api should get StageName from globals
        let stage = get_resource_prop(&merged, "MyApi", "StageName").unwrap();
        assert_eq!(stage.as_str(), Some("prod"));

        // Api should NOT get Function globals
        let api_timeout = get_resource_prop(&merged, "MyApi", "Timeout");
        assert!(api_timeout.is_none());
    }

    #[test]
    fn test_non_serverless_resources_unchanged() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Function should get Timeout
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(30.0));

        // S3 Bucket should be unchanged (no Timeout property)
        let bucket_timeout = get_resource_prop(&merged, "MyBucket", "Timeout");
        assert!(bucket_timeout.is_none());

        // Bucket should keep its BucketName
        let bucket_name = get_resource_prop(&merged, "MyBucket", "BucketName").unwrap();
        assert_eq!(bucket_name.as_str(), Some("my-bucket"));
    }

    #[test]
    fn test_preserves_spans() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 60
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // The local Timeout should preserve its span
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        // Span should not be default (0,0)
        let span = timeout.span();
        // Original YAML has Timeout on a specific line
        assert!(span.start.line > 0 || span.start.column > 0);
    }

    #[test]
    fn test_type_mismatch_local_wins() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout:
      - item1
      - item2
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 60
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Local number should win over global array
        let timeout = get_resource_prop(&merged, "MyFunction", "Timeout").unwrap();
        assert_eq!(timeout.as_f64(), Some(60.0));
    }

    #[test]
    fn test_all_globals_types() {
        // Test all resource types in GLOBALS_TYPE_MAP
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
  Api:
    StageName: prod
  HttpApi:
    StageName: v1
  SimpleTable:
    SSESpecification:
      SSEEnabled: true
  StateMachine:
    Tracing:
      Enabled: true
  LayerVersion:
    CompatibleRuntimes:
      - python3.9
  CapacityProvider:
    AutoScalingGroupProvider:
      ManagedScaling:
        Status: ENABLED
  WebSocketApi:
    StageName: production
Resources:
  Fn:
    Type: AWS::Serverless::Function
    Properties:
      Handler: h
  Api:
    Type: AWS::Serverless::Api
    Properties:
      Name: api
  HttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      Name: httpapi
  Table:
    Type: AWS::Serverless::SimpleTable
    Properties:
      TableName: tbl
  SM:
    Type: AWS::Serverless::StateMachine
    Properties:
      Name: sm
  Layer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: layer
"#;
        let root = parse_yaml(yaml);
        let merged = merge_globals(&root);

        // Function
        assert_eq!(
            get_resource_prop(&merged, "Fn", "Timeout")
                .unwrap()
                .as_f64(),
            Some(30.0)
        );

        // Api
        assert_eq!(
            get_resource_prop(&merged, "Api", "StageName")
                .unwrap()
                .as_str(),
            Some("prod")
        );

        // HttpApi
        assert_eq!(
            get_resource_prop(&merged, "HttpApi", "StageName")
                .unwrap()
                .as_str(),
            Some("v1")
        );

        // SimpleTable
        let sse = get_resource_prop(&merged, "Table", "SSESpecification").unwrap();
        assert_eq!(sse.get("SSEEnabled").unwrap().as_bool(), Some(true));

        // StateMachine
        let tracing = get_resource_prop(&merged, "SM", "Tracing").unwrap();
        assert_eq!(tracing.get("Enabled").unwrap().as_bool(), Some(true));

        // LayerVersion
        let runtimes = get_resource_prop(&merged, "Layer", "CompatibleRuntimes")
            .unwrap()
            .as_array()
            .unwrap();
        assert_eq!(runtimes.elements[0].as_str(), Some("python3.9"));
    }
}
