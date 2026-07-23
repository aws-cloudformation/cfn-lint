use crate::ast::AstNode;
use crate::graph::{EdgeKind, Graph};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W3005;

impl CfnLintRule for W3005 {
    fn id(&self) -> &str {
        "W3005"
    }
    fn short_description(&self) -> &str {
        "Check obsolete DependsOn configuration for Resources"
    }
    fn description(&self) -> &str {
        "DependsOn is not needed when an implicit dependency exists via Ref or Fn::GetAtt"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/DependsOn", "Resources/*/DependsOn/*"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // We only process individual string DependsOn values
        let dep_name = match instance.as_str() {
            Some(s) => s,
            None => {
                // If this is an array (DependsOn: [A, B]), we handle each element
                // via the Resources/*/DependsOn/* keyword path
                return vec![];
            }
        };

        // Get the source resource name from path: ["Resources", "<name>", "DependsOn", ...]
        let from_resource_name = match path.get(1) {
            Some(name) => name.as_str(),
            None => return vec![],
        };

        // We need context to access the template for graph building
        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        let template = &ctx.template;
        let root = &template.root;

        let graph = Graph::build(template, root);
        let implicit = graph.implicit_deps(from_resource_name);

        if !implicit.contains(dep_name) {
            return vec![];
        }

        // Find the implicit edges for the error message
        let mut errors = Vec::new();
        for edge in &graph.edges {
            if edge.source != from_resource_name
                || edge.target != dep_name
                || edge.kind == EdgeKind::DependsOn
            {
                continue;
            }
            let mut full_path = vec!["Resources".to_string(), from_resource_name.to_string()];
            full_path.extend(edge.source_path.clone());
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} dependency already enforced by a {:?} at {:?}",
                    dep_name,
                    edge.kind.label(),
                    full_path.join("/"),
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
        errors
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_depends_on_with_ref_stub() {
        let yaml = br#"
Resources:
  Topic:
    Type: AWS::SNS::Topic
  Bucket:
    Type: AWS::S3::Bucket
    DependsOn: Topic
    Properties:
      BucketName: !Ref Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3005.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_depends_on_without_ref_ok() {
        let yaml = br#"
Resources:
  Topic:
    Type: AWS::SNS::Topic
  Bucket:
    Type: AWS::S3::Bucket
    DependsOn: Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3005.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W3005);
