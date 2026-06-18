use crate::ast::{AstNode, Span};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::transform::is_sam_template;

/// E0001: Error found when transforming the template.
///
/// Validates SAM serverless resources for required properties and
/// event source configurations that would cause the SAM translator to fail.
pub struct E0001;

/// Required properties for SAM resource types.
const SAM_REQUIRED: &[(&str, &[&str])] = &[
    ("AWS::Serverless::Api", &["StageName"]),
    ("AWS::Serverless::Application", &["Location"]),
    ("AWS::Serverless::LayerVersion", &["ContentUri"]),
    ("AWS::Serverless::Connector", &["Source", "Destination", "Permissions"]),
];

/// Required properties for SAM event types (under Function Events).
const SAM_EVENT_REQUIRED: &[(&str, &[&str])] = &[
    ("Schedule", &["Schedule"]),
    ("CloudWatchEvent", &["Pattern"]),
    ("EventBridgeRule", &["Pattern"]),
    ("S3", &["Bucket", "Events"]),
    ("SNS", &["Topic"]),
    ("SQS", &["Queue"]),
    ("Kinesis", &["Stream", "StartingPosition"]),
    ("DynamoDB", &["Stream", "StartingPosition"]),
    ("Api", &["Path", "Method"]),
    ("HttpApi", &["Path", "Method"]),
];

impl CfnLintRule for E0001 {
    fn id(&self) -> &str { "E0001" }
    fn short_description(&self) -> &str { "Error found when transforming the template" }
    fn description(&self) -> &str {
        "Errors found when performing transformation on the template"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        if !is_sam_template(root) {
            return vec![];
        }

        let mut issues = Vec::new();

        for (name, resource) in &template.resources {
            // Check required properties for SAM resource types
            for &(rtype, required) in SAM_REQUIRED {
                if resource.resource_type != rtype {
                    continue;
                }
                let props = resource.properties.as_ref().and_then(|p| p.as_object());
                for &req in required {
                    let missing = match &props {
                        Some(obj) => !obj.contains_key(req),
                        None => true,
                    };
                    if missing {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "Error transforming template: Resource with id [{}] is invalid. Missing required property '{}'.",
                                name, req
                            ),
                            path: vec!["Resources".into(), name.clone()],
                            span: Span::default(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
});
                    }
                }
            }

            // Check SAM Function event sources
            if resource.resource_type == "AWS::Serverless::Function" {
                if let Some(events) = resource.properties.as_ref()
                    .and_then(|p| p.get("Events"))
                    .and_then(|e| e.as_object())
                {
                    for (event_name, event_node) in events.iter() {
                        let event_type = event_node.get("Type").and_then(|t| t.as_str());
                        let event_props = event_node.get("Properties").and_then(|p| p.as_object());

                        if let Some(etype) = event_type {
                            for &(sam_etype, required) in SAM_EVENT_REQUIRED {
                                if etype != sam_etype { continue; }
                                for &req in required {
                                    let missing = match &event_props {
                                        Some(obj) => !obj.contains_key(req),
                                        None => true,
                                    };
                                    if missing {
                                        // SAM translator uses a composite resource ID for events
                                        issues.push(ValidationError {
                                            rule_id: Some(self.id().to_string()),
                                            message: format!(
                                                "Error transforming template: Resource with id [{}{}] is invalid. Missing required property '{}'.",
                                                name, event_name, req
                                            ),
                                            path: vec![
                                                "Resources".into(), name.clone(),
                                                "Properties".into(), "Events".into(),
                                                event_name.to_string(),
                                            ],
                                            span: Span::default(),
                                            keyword: String::new(),
                                            unknown: false,
                                            resolved_from_ref: false,
                                            context: vec![],
                                            schema_id: None,
});
                                    }
                                }
                            }
                        }
                    }
                }

                // Validate AutoPublishAlias: must be a string or Ref
                if let Some(apa) = resource.properties.as_ref()
                    .and_then(|p| p.get("AutoPublishAlias"))
                {
                    match apa {
                        AstNode::String(_) => {} // valid
                        AstNode::Function(f) if f.name == "Ref" => {} // valid
                        AstNode::Object(obj) => {
                            // Check if it's a single-key Ref
                            if obj.len() == 1 && obj.contains_key("Ref") {
                                // valid Ref
                            } else if obj.len() == 1 {
                                issues.push(ValidationError {
                                    rule_id: Some(self.id().to_string()),
                                    message: format!(
                                        "Error transforming template: Resource with id [{}] is invalid. \
                                         'AutoPublishAlias' must be a string or a Ref to a template parameter",
                                        name
                                    ),
                                    path: vec!["Resources".into(), name.clone(), "Properties".into(), "AutoPublishAlias".into()],
                                    span: Span::default(),
                                    keyword: String::new(),
                                    unknown: false,
                                    resolved_from_ref: false,
                                    context: vec![],
                                    schema_id: None,
});
                            } else {
                                // Multiple keys — invalid type
                                issues.push(ValidationError {
                                    rule_id: Some(self.id().to_string()),
                                    message: format!(
                                        "Error transforming template: Resource with id [{}] is invalid. \
                                         Type of property 'AutoPublishAlias' is invalid.",
                                        name
                                    ),
                                    path: vec!["Resources".into(), name.clone(), "Properties".into(), "AutoPublishAlias".into()],
                                    span: Span::default(),
                                    keyword: String::new(),
                                    unknown: false,
                                    resolved_from_ref: false,
                                    context: vec![],
                                    schema_id: None,
});
                            }
                        }
                        _ => {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "Error transforming template: Resource with id [{}] is invalid. \
                                     'AutoPublishAlias' must be a string or a Ref to a template parameter",
                                    name
                                ),
                                path: vec!["Resources".into(), name.clone(), "Properties".into(), "AutoPublishAlias".into()],
                                span: Span::default(),
                                keyword: String::new(),
                                unknown: false,
                                resolved_from_ref: false,
                                context: vec![],
                                schema_id: None,
});
                        }
                    }
                }
            }
        }
        issues
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{ObjectNode, Span};
    use indexmap::IndexMap;

    fn empty_template() -> (Template, AstNode) {
        let root = AstNode::Object(ObjectNode { entries: Vec::new(), span: Span::default() });
        let tmpl = Template::from_ast(&root).unwrap();
        (tmpl, root)
    }

    #[test]
    fn test_metadata() {
        assert_eq!(E0001.id(), "E0001");
        assert_eq!(E0001.severity(), Severity::Error);
    }

    #[test]
    fn test_validate_returns_empty_non_sam() {
        let (tmpl, root) = empty_template();
        assert!(E0001.validate_template(&tmpl, &root).is_empty());
    }
}

crate::register_cfn_lint_rule!(E0001);
