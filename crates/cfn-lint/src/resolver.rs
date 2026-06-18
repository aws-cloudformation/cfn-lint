use crate::ast::AstNode;
use crate::context::Context;
use crate::jsonschema::resolvers;

/// Single-value resolver: thin wrapper around the multi-value `resolvers::resolve_value`.
/// Returns the first possible resolved value (useful when callers only need one answer).
pub struct Resolver<'a> {
    ctx: &'a Context,
}

impl<'a> Resolver<'a> {
    pub fn new(ctx: &'a Context) -> Self {
        Resolver { ctx }
    }

    /// Resolve an AstNode. Non-function nodes pass through.
    /// Returns None if the function cannot be resolved.
    pub fn resolve(&self, node: &AstNode) -> Option<AstNode> {
        let results = resolvers::resolve_value(self.ctx, node);
        results.into_iter().next().map(|r| r.value)
    }

    /// Convenience: resolve a node and extract its string value.
    pub fn resolve_string(&self, node: &AstNode) -> Option<String> {
        self.resolve(node)
            .and_then(|n| n.as_str().map(String::from))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    fn make_ctx(yaml: &[u8]) -> Context {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        Context::new(tmpl)
    }

    fn str_node(s: &str) -> AstNode {
        AstNode::String(StringNode {
            value: s.to_string(),
            span: Span::default(),
        })
    }

    fn num_node(n: f64) -> AstNode {
        AstNode::Number(NumberNode {
            value: n,
            span: Span::default(),
        })
    }

    fn func_node(name: &str, args: AstNode) -> AstNode {
        AstNode::Function(FunctionNode {
            name: name.to_string(),
            args: Box::new(args),
            span: Span::default(),
        })
    }

    fn arr_node(elements: Vec<AstNode>) -> AstNode {
        AstNode::Array(ArrayNode {
            elements,
            span: Span::default(),
        })
    }

    #[test]
    fn test_non_function_passthrough() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = str_node("hello");
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("hello"));
    }

    #[test]
    fn test_resolve_ref_pseudo() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node("Ref", str_node("AWS::Region"));
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("us-east-1"));
    }

    #[test]
    fn test_resolve_ref_parameter() {
        let ctx = make_ctx(
            br#"
Parameters:
  Env:
    Type: String
    Default: prod
Resources:
  X:
    Type: AWS::SNS::Topic
"#,
        );
        let r = Resolver::new(&ctx);
        let node = func_node("Ref", str_node("Env"));
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("prod"));
    }

    #[test]
    fn test_resolve_ref_unresolvable() {
        let ctx = make_ctx(
            br#"
Parameters:
  Env:
    Type: String
Resources:
  X:
    Type: AWS::SNS::Topic
"#,
        );
        let r = Resolver::new(&ctx);
        let node = func_node("Ref", str_node("Env"));
        // Parameter with no Default and no AllowedValues still resolves
        // via the multi-value resolver (it may return dynamic values).
        // The old resolver returned None; the new one delegates to resolve_value
        // which returns all scenarios from context.resolve_ref.
        // A param with no constraints returns no scenarios → None.
        assert!(r.resolve(&node).is_none());
    }

    #[test]
    fn test_resolve_join() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::Join",
            arr_node(vec![
                str_node("-"),
                arr_node(vec![str_node("a"), str_node("b"), str_node("c")]),
            ]),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("a-b-c"));
    }

    #[test]
    fn test_resolve_join_empty_delimiter() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::Join",
            arr_node(vec![
                str_node(""),
                arr_node(vec![str_node("x"), str_node("y")]),
            ]),
        );
        assert_eq!(r.resolve(&node).unwrap().as_str(), Some("xy"));
    }

    #[test]
    fn test_resolve_select() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::Select",
            arr_node(vec![
                num_node(1.0),
                arr_node(vec![str_node("a"), str_node("b"), str_node("c")]),
            ]),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("b"));
    }

    #[test]
    fn test_resolve_split() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::Split",
            arr_node(vec![str_node(","), str_node("a,b,c")]),
        );
        let result = r.resolve(&node).unwrap();
        let arr = result.as_array().unwrap();
        let vals: Vec<&str> = arr.elements.iter().filter_map(|e| e.as_str()).collect();
        assert_eq!(vals, vec!["a", "b", "c"]);
    }

    #[test]
    fn test_resolve_sub_string_form() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::Sub",
            str_node("arn:${AWS::Partition}:s3:::${AWS::AccountId}"),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("arn:aws:s3:::123456789012"));
    }

    #[test]
    fn test_resolve_sub_array_form() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);

        let mut map_props: Vec<ObjectEntry> = Vec::new();
        map_props.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "MyVar".to_string(),
                span: Span::default(),
            }),
            key: "MyVar".to_string(),
            value: str_node("custom-value"),
            key_span: Span::default(),
        });
        let map_node = AstNode::Object(ObjectNode {
            entries: map_props,
            span: Span::default(),
        });

        let node = func_node(
            "Fn::Sub",
            arr_node(vec![str_node("prefix-${MyVar}-${AWS::Region}"), map_node]),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("prefix-custom-value-us-east-1"));
    }

    #[test]
    fn test_resolve_if_known_condition() {
        let mut ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        ctx.condition_state.insert("IsProd".to_string(), true);
        let r = Resolver::new(&ctx);

        let node = func_node(
            "Fn::If",
            arr_node(vec![
                str_node("IsProd"),
                str_node("prod-value"),
                str_node("dev-value"),
            ]),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("prod-value"));
    }

    #[test]
    fn test_resolve_if_false_condition() {
        let mut ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        ctx.condition_state.insert("IsProd".to_string(), false);
        let r = Resolver::new(&ctx);

        let node = func_node(
            "Fn::If",
            arr_node(vec![
                str_node("IsProd"),
                str_node("prod-value"),
                str_node("dev-value"),
            ]),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("dev-value"));
    }

    #[test]
    fn test_resolve_if_unknown_condition() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);

        let node = func_node(
            "Fn::If",
            arr_node(vec![
                str_node("IsProd"),
                str_node("prod-value"),
                str_node("dev-value"),
            ]),
        );
        // Unknown condition → multi-value resolver returns both branches.
        // The single-value wrapper takes the first (true branch).
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("prod-value"));
    }

    #[test]
    fn test_resolve_find_in_map() {
        let ctx = make_ctx(
            br#"
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345678
    eu-west-1:
      AMI: ami-87654321
Resources:
  X:
    Type: AWS::SNS::Topic
"#,
        );
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::FindInMap",
            arr_node(vec![
                str_node("RegionMap"),
                str_node("us-east-1"),
                str_node("AMI"),
            ]),
        );
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("ami-12345678"));
    }

    #[test]
    fn test_resolve_find_in_map_missing_key() {
        let ctx = make_ctx(
            br#"
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345678
Resources:
  X:
    Type: AWS::SNS::Topic
"#,
        );
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::FindInMap",
            arr_node(vec![
                str_node("RegionMap"),
                str_node("ap-southeast-1"),
                str_node("AMI"),
            ]),
        );
        assert!(r.resolve(&node).is_none());
    }

    #[test]
    fn test_resolve_base64_passthrough() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node("Fn::Base64", str_node("hello"));
        let result = r.resolve(&node).unwrap();
        assert_eq!(result.as_str(), Some("hello"));
    }

    #[test]
    fn test_resolve_getazs_returns_values() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node("Fn::GetAZs", str_node("us-east-1"));
        // The multi-value resolver actually resolves GetAZs to AZ lists.
        let result = r.resolve(&node).unwrap();
        let arr = result.as_array().unwrap();
        assert_eq!(arr.elements[0].as_str(), Some("us-east-1a"));
    }

    #[test]
    fn test_resolve_getatt_returns_none() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node(
            "Fn::GetAtt",
            arr_node(vec![str_node("MyBucket"), str_node("Arn")]),
        );
        assert!(r.resolve(&node).is_none());
    }

    #[test]
    fn test_resolve_string_convenience() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = func_node("Ref", str_node("AWS::Partition"));
        assert_eq!(r.resolve_string(&node), Some("aws".to_string()));
    }

    #[test]
    fn test_resolve_string_non_string_returns_none() {
        let ctx = make_ctx(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let r = Resolver::new(&ctx);
        let node = num_node(42.0);
        assert!(r.resolve_string(&node).is_none());
    }
}
