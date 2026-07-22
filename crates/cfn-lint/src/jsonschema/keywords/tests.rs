use super::super::ValidationError;
use super::super::Validator;
use super::helpers::*;
use super::*;
use crate::ast::{
    ArrayNode, AstNode, FunctionNode, NumberNode, ObjectEntry, ObjectNode, Position, Span,
    StringNode,
};

fn pos() -> Span {
    Span {
        start: Position { line: 1, column: 1 },
        end: Position { line: 1, column: 1 },
    }
}

fn str_node(s: &str) -> AstNode {
    AstNode::String(StringNode {
        value: s.to_string(),
        span: pos(),
    })
}

fn make_validator() -> Validator {
    Validator::new(serde_json::json!({}))
}

fn make_strict_validator() -> Validator {
    Validator::new_strict(serde_json::json!({}))
}

fn run_format(node: &AstNode, format: &str) -> Vec<ValidationError> {
    let v = make_validator();
    let constraint = serde_json::Value::String(format.to_string());
    let schema = serde_json::json!({});
    validate_format(&v, node, &constraint, &schema, &[])
}

// --- AMI ID ---
#[test]
fn test_format_ami_valid_short() {
    assert!(run_format(&str_node("ami-12345678"), "AWS::EC2::Image.Id").is_empty());
}

#[test]
fn test_format_ami_valid_long() {
    assert!(run_format(&str_node("ami-0123456789abcdef0"), "AWS::EC2::Image.Id").is_empty());
}

#[test]
fn test_format_ami_invalid() {
    assert_eq!(
        run_format(&str_node("i-12345678"), "AWS::EC2::Image.Id").len(),
        1
    );
}

#[test]
fn test_format_ami_invalid_uppercase() {
    // Uppercase letters beyond 'f' are not in [0-9a-z]
    assert_eq!(
        run_format(&str_node("ami-ABCDEF12"), "AWS::EC2::Image.Id").len(),
        1
    );
}

#[test]
fn test_format_ami_too_short() {
    assert_eq!(
        run_format(&str_node("ami-1234567"), "AWS::EC2::Image.Id").len(),
        1
    );
}

// --- Security Group ID ---
#[test]
fn test_format_sg_valid() {
    assert!(run_format(&str_node("sg-12345678"), "AWS::EC2::SecurityGroup.Id").is_empty());
}

#[test]
fn test_format_sg_valid_long() {
    assert!(run_format(
        &str_node("sg-0123456789abcdef0"),
        "AWS::EC2::SecurityGroup.Id"
    )
    .is_empty());
}

#[test]
fn test_format_sg_invalid() {
    assert_eq!(
        run_format(&str_node("vpc-12345678"), "AWS::EC2::SecurityGroup.Id").len(),
        1
    );
}

#[test]
fn test_format_sg_invalid_value() {
    assert_eq!(
        run_format(&str_node("sg-dne"), "AWS::EC2::SecurityGroup.Id").len(),
        1
    );
}

// --- Subnet ID ---
#[test]
fn test_format_subnet_valid() {
    assert!(run_format(&str_node("subnet-12345678"), "AWS::EC2::Subnet.Id").is_empty());
}

#[test]
fn test_format_subnet_invalid() {
    assert_eq!(
        run_format(&str_node("sub-12345678"), "AWS::EC2::Subnet.Id").len(),
        1
    );
}

// --- VPC ID ---
#[test]
fn test_format_vpc_valid() {
    assert!(run_format(&str_node("vpc-12345678"), "AWS::EC2::VPC.Id").is_empty());
}

#[test]
fn test_format_vpc_invalid() {
    assert_eq!(
        run_format(&str_node("sg-12345678"), "AWS::EC2::VPC.Id").len(),
        1
    );
}

// --- Security Group Name ---
#[test]
fn test_format_sg_name_valid() {
    assert!(run_format(
        &str_node("my-security-group"),
        "AWS::EC2::SecurityGroup.Name"
    )
    .is_empty());
}

#[test]
fn test_format_sg_name_empty() {
    assert_eq!(
        run_format(&str_node(""), "AWS::EC2::SecurityGroup.Name").len(),
        1
    );
}

#[test]
fn test_format_sg_name_invalid_chars() {
    assert_eq!(
        run_format(&str_node("sg\ttab"), "AWS::EC2::SecurityGroup.Name").len(),
        1
    );
}

// --- IAM Role ARN ---
#[test]
fn test_format_iam_role_arn_valid() {
    assert!(run_format(
        &str_node("arn:aws:iam::123456789012:role/MyRole"),
        "AWS::IAM::Role.Arn"
    )
    .is_empty());
}

#[test]
fn test_format_iam_role_arn_invalid() {
    assert_eq!(
        run_format(&str_node("arn:aws:s3:::my-bucket"), "AWS::IAM::Role.Arn").len(),
        1
    );
}

// --- Log Group Name ---
#[test]
fn test_format_log_group_valid() {
    assert!(run_format(
        &str_node("/aws/lambda/my-function"),
        "AWS::Logs::LogGroup.Name"
    )
    .is_empty());
}

#[test]
fn test_format_log_group_valid_with_hash() {
    assert!(run_format(&str_node("my#log.group_name-1"), "AWS::Logs::LogGroup.Name").is_empty());
}

#[test]
fn test_format_log_group_invalid_chars() {
    assert_eq!(
        run_format(&str_node("log group!"), "AWS::Logs::LogGroup.Name").len(),
        1
    );
}

#[test]
fn test_format_log_group_too_long() {
    let long = "a".repeat(513);
    assert_eq!(
        run_format(&str_node(&long), "AWS::Logs::LogGroup.Name").len(),
        1
    );
}

#[test]
fn test_format_log_group_max_length() {
    let max = "a".repeat(512);
    assert!(run_format(&str_node(&max), "AWS::Logs::LogGroup.Name").is_empty());
}

// --- Unknown format ---
#[test]
fn test_format_unknown_skipped() {
    assert!(run_format(&str_node("anything"), "AWS::Custom::Unknown").is_empty());
}

// --- Non-string nodes ---
#[test]
fn test_format_non_string_skipped() {
    let num = AstNode::Number(NumberNode {
        value: 42.0,
        span: pos(),
    });
    assert!(run_format(&num, "AWS::EC2::Image.Id").is_empty());
}

#[test]
fn test_format_function_skipped() {
    let func = AstNode::Function(FunctionNode {
        name: "Ref".to_string(),
        args: Box::new(str_node("Param")),
        span: pos(),
    });
    assert!(run_format(&func, "AWS::EC2::Image.Id").is_empty());
}

// --- Error keyword ---
#[test]
fn test_format_error_keyword() {
    let errs = run_format(&str_node("bad"), "AWS::EC2::Image.Id");
    assert!(errs[0].keyword.starts_with("format:"));
}

// ===== New keyword tests =====

fn num_node(n: f64) -> AstNode {
    AstNode::Number(NumberNode {
        value: n,
        span: pos(),
    })
}

fn obj_node(props: Vec<(&str, AstNode)>) -> AstNode {
    let mut map: Vec<ObjectEntry> = Vec::new();
    for (k, v) in props {
        map.push(ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: k.to_string(),
                span: Span::default(),
            }),
            key: k.to_string(),
            value: v,
            key_span: Span::default(),
        });
    }
    AstNode::Object(ObjectNode {
        entries: map,
        span: pos(),
    })
}

fn arr_node(elems: Vec<AstNode>) -> AstNode {
    AstNode::Array(ArrayNode {
        elements: elems,
        span: pos(),
    })
}

// --- dependentExcluded ---
#[test]
fn test_dependent_excluded_trigger_absent() {
    let v = make_validator();
    let constraint = serde_json::json!({"A": ["B"]});
    let node = obj_node(vec![("C", str_node("1"))]);
    assert!(
        validate_dependent_excluded(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty()
    );
}

#[test]
fn test_dependent_excluded_no_conflict() {
    let v = make_validator();
    let constraint = serde_json::json!({"A": ["B"]});
    let node = obj_node(vec![("A", str_node("1")), ("C", str_node("2"))]);
    assert!(
        validate_dependent_excluded(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty()
    );
}

#[test]
fn test_dependent_excluded_conflict() {
    let v = make_validator();
    let constraint = serde_json::json!({"A": ["B", "C"]});
    let node = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
    let errs = validate_dependent_excluded(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "dependentExcluded");
    assert!(errs[0].message.contains("\"B\""));
}

#[test]
fn test_dependent_excluded_multiple_conflicts() {
    let v = make_validator();
    let constraint = serde_json::json!({"A": ["B", "C"]});
    let node = obj_node(vec![
        ("A", str_node("1")),
        ("B", str_node("2")),
        ("C", str_node("3")),
    ]);
    let errs = validate_dependent_excluded(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 2);
}

// --- maxProperties ---
#[test]
fn test_max_properties_valid() {
    let v = make_validator();
    let node = obj_node(vec![("A", str_node("1"))]);
    assert!(validate_max_properties(
        &v,
        &node,
        &serde_json::json!(2),
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_max_properties_exceeded() {
    let v = make_validator();
    let node = obj_node(vec![
        ("A", str_node("1")),
        ("B", str_node("2")),
        ("C", str_node("3")),
    ]);
    let errs = validate_max_properties(
        &v,
        &node,
        &serde_json::json!(2),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "maxProperties");
}

// --- minProperties ---
#[test]
fn test_min_properties_valid() {
    let v = make_validator();
    let node = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
    assert!(validate_min_properties(
        &v,
        &node,
        &serde_json::json!(2),
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_min_properties_too_few() {
    let v = make_validator();
    let node = obj_node(vec![("A", str_node("1"))]);
    let errs = validate_min_properties(
        &v,
        &node,
        &serde_json::json!(2),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "minProperties");
}

// --- propertyNames ---
#[test]
fn test_property_names_valid() {
    let v = make_validator();
    let constraint = serde_json::json!({"pattern": "^[a-z]+$"});
    let node = obj_node(vec![("abc", str_node("1")), ("def", str_node("2"))]);
    assert!(
        validate_property_names(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty()
    );
}

#[test]
fn test_property_names_invalid() {
    let v = make_validator();
    let constraint = serde_json::json!({"pattern": "^[a-z]+$"});
    let node = obj_node(vec![("abc", str_node("1")), ("ABC", str_node("2"))]);
    let errs = validate_property_names(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
}

// --- contains ---
#[test]
fn test_contains_valid() {
    let v = make_validator();
    let constraint = serde_json::json!({"type": "string"});
    let node = arr_node(vec![num_node(1.0), str_node("hello")]);
    assert!(validate_contains(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_contains_no_match() {
    let v = make_strict_validator();
    let constraint = serde_json::json!({"type": "string"});
    let node = arr_node(vec![num_node(1.0), num_node(2.0)]);
    let errs = validate_contains(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "contains");
}

// --- prefixItems ---
#[test]
fn test_prefix_items_valid() {
    let v = make_validator();
    let constraint = serde_json::json!([{"type": "string"}, {"type": "integer"}]);
    let node = arr_node(vec![str_node("hello"), num_node(42.0)]);
    assert!(validate_prefix_items(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_prefix_items_invalid() {
    let v = make_strict_validator();
    let constraint = serde_json::json!([{"type": "string"}, {"type": "integer"}]);
    let node = arr_node(vec![num_node(1.0), str_node("bad")]);
    let errs = validate_prefix_items(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 2);
}

#[test]
fn test_prefix_items_extra_elements_ignored() {
    let v = make_validator();
    let constraint = serde_json::json!([{"type": "string"}]);
    let node = arr_node(vec![str_node("ok"), num_node(99.0)]);
    assert!(validate_prefix_items(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

// --- uniqueKeys ---
#[test]
fn test_unique_keys_valid() {
    let v = make_validator();
    let constraint = serde_json::json!(["Name"]);
    let node = arr_node(vec![
        obj_node(vec![("Name", str_node("a"))]),
        obj_node(vec![("Name", str_node("b"))]),
    ]);
    assert!(validate_unique_keys(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_unique_keys_duplicate() {
    let v = make_validator();
    let constraint = serde_json::json!(["Name"]);
    let node = arr_node(vec![
        obj_node(vec![("Name", str_node("a"))]),
        obj_node(vec![("Name", str_node("a"))]),
    ]);
    let errs = validate_unique_keys(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "uniqueKeys");
}

// --- multipleOf ---
#[test]
fn test_multiple_of_valid() {
    let v = make_validator();
    assert!(validate_multiple_of(
        &v,
        &num_node(10.0),
        &serde_json::json!(5),
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_multiple_of_invalid() {
    let v = make_validator();
    let errs = validate_multiple_of(
        &v,
        &num_node(7.0),
        &serde_json::json!(3),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "multipleOf");
}

#[test]
fn test_multiple_of_float() {
    let v = make_validator();
    assert!(validate_multiple_of(
        &v,
        &num_node(0.3),
        &serde_json::json!(0.1),
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

// --- requiredXor ---
#[test]
fn test_required_xor_exactly_one() {
    let v = make_validator();
    let constraint = serde_json::json!(["A", "B"]);
    let node = obj_node(vec![("A", str_node("1"))]);
    assert!(validate_required_xor(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_required_xor_none() {
    let v = make_validator();
    let constraint = serde_json::json!(["A", "B"]);
    let node = obj_node(vec![("C", str_node("1"))]);
    let errs = validate_required_xor(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "requiredXor");
}

#[test]
fn test_required_xor_multiple() {
    let v = make_validator();
    let constraint = serde_json::json!(["A", "B"]);
    let node = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
    let errs = validate_required_xor(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 2);
}

// --- requiredOr ---
#[test]
fn test_required_or_one_present() {
    let v = make_validator();
    let constraint = serde_json::json!(["A", "B"]);
    let node = obj_node(vec![("A", str_node("1"))]);
    assert!(validate_required_or(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_required_or_both_present() {
    let v = make_validator();
    let constraint = serde_json::json!(["A", "B"]);
    let node = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
    assert!(validate_required_or(&v, &node, &constraint, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_required_or_none_present() {
    let v = make_validator();
    let constraint = serde_json::json!(["A", "B"]);
    let node = obj_node(vec![("C", str_node("1"))]);
    let errs = validate_required_or(&v, &node, &constraint, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "requiredOr");
}

// --- enumCaseInsensitive ---
#[test]
fn test_enum_case_insensitive_match() {
    let v = make_validator();
    let constraint = serde_json::json!(["Enabled", "Disabled"]);
    assert!(validate_enum_case_insensitive(
        &v,
        &str_node("enabled"),
        &constraint,
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_enum_case_insensitive_exact() {
    let v = make_validator();
    let constraint = serde_json::json!(["Enabled", "Disabled"]);
    assert!(validate_enum_case_insensitive(
        &v,
        &str_node("Enabled"),
        &constraint,
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_enum_case_insensitive_no_match() {
    let v = make_validator();
    let constraint = serde_json::json!(["Enabled", "Disabled"]);
    let errs = validate_enum_case_insensitive(
        &v,
        &str_node("Unknown"),
        &constraint,
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "enumCaseInsensitive");
    assert!(errs[0].message.contains("case-insensitive"));
}

#[test]
fn test_enum_case_insensitive_non_string() {
    let v = make_validator();
    let constraint = serde_json::json!([1, 2, 3]);
    assert!(validate_enum_case_insensitive(
        &v,
        &num_node(2.0),
        &constraint,
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

// --- cfn_context tests ---

mod cfn_context_tests {
    use super::*;
    use crate::context::Context;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    #[test]
    fn test_cfn_context_rejects_disallowed_function() {
        let yaml = br#"
Conditions:
  C: !Equals [!Ref AWS::Region, !ImportValue PrimaryRegion]
Resources:
  D:
    Type: AWS::SNS::Topic
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(Arc::clone(&tmpl)).evolve(crate::context::ContextOptions {
            functions: Some(vec![
                "Fn::Equals".into(),
                "Fn::And".into(),
                "Fn::Or".into(),
                "Fn::Not".into(),
                "Condition".into(),
            ]),
            ..Default::default()
        });

        let equals_schema: serde_json::Value = serde_json::from_str(include_str!(
            "../../../data/schemas/other/functions/equals.json"
        ))
        .unwrap();

        // Get the Fn::Equals args (the array [!Ref, !ImportValue])
        let cond = ast.get("Conditions").unwrap().get("C").unwrap();
        let args = cond
            .as_function()
            .expect("should be Function node")
            .args
            .as_ref();

        let v = Validator::new_with_context(serde_json::json!({}), Arc::new(ctx));
        let errs = v.validate_schema(args, &equals_schema, &["Conditions".into(), "C".into()]);
        let real_errs: Vec<_> = errs.into_iter().filter(|e| !e.unknown).collect();
        eprintln!("Errors: {}", real_errs.len());
        for _e in &real_errs {}
        assert!(
            !real_errs.is_empty(),
            "Should have errors for disallowed ImportValue"
        );
    }
}

mod findinmap_structure_tests {
    use super::*;
    use crate::context::Context;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    #[test]
    fn test_findinmap_rejects_getatt_arg() {
        let yaml = br#"
Mappings:
  amimap:
    us-east-1:
      AMI: ami-12345
Resources:
  myInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [amimap, !Ref "AWS::Region", !GetAtt myInstance.AvailabilityZone]
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(Arc::clone(&tmpl));
        let v = Validator::new_with_context(serde_json::json!({}), Arc::new(ctx));

        let findinmap = ast
            .get("Resources")
            .unwrap()
            .get("myInstance")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("ImageId")
            .unwrap();
        let func = findinmap.as_function().expect("should be FindInMap");

        let errs = validate_function_structure(&v, "Fn::FindInMap", &func.args, &["test".into()]);
        eprintln!("FindInMap structure errors: {}", errs.len());
        for _e in &errs {}
        assert!(!errs.is_empty(), "Should reject GetAtt inside FindInMap");
    }
}

// ===== C19: minLength/maxLength count Unicode code points, not bytes =====

#[test]
fn test_min_length_unicode_counts_code_points() {
    // '日本' is 2 code points but 6 UTF-8 bytes.
    let v = make_validator();
    let node = str_node("日本");
    // len()==6 would satisfy minLength 3; chars().count()==2 must not.
    let errs = validate_min_length(
        &v,
        &node,
        &serde_json::json!(3),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "minLength");
    assert!(
        errs[0].message.contains("found: 2"),
        "msg: {}",
        errs[0].message
    );
}

#[test]
fn test_min_length_unicode_exactly_meets() {
    let v = make_validator();
    let node = str_node("日本");
    assert!(validate_min_length(
        &v,
        &node,
        &serde_json::json!(2),
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_max_length_unicode_counts_code_points() {
    // 2 code points is within maxLength 2, even though it is 6 bytes.
    let v = make_validator();
    let node = str_node("日本");
    assert!(validate_max_length(
        &v,
        &node,
        &serde_json::json!(2),
        &serde_json::json!({}),
        &[]
    )
    .is_empty());
}

#[test]
fn test_max_length_unicode_exceeded() {
    let v = make_validator();
    let node = str_node("日本");
    let errs = validate_max_length(
        &v,
        &node,
        &serde_json::json!(1),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "maxLength");
    assert!(
        errs[0].message.contains("found: 2"),
        "msg: {}",
        errs[0].message
    );
}

// ===== C23: const/enum number equality is exact, not epsilon-based =====

#[test]
fn test_const_equality_distinct_near_zero_values_differ() {
    // Distinct near-zero values must NOT compare equal. An epsilon comparison
    // (< f64::EPSILON) wrongly treats these as equal.
    assert!(!ast_matches_json(
        &num_node(1e-20),
        &serde_json::json!(2e-20)
    ));
}

#[test]
fn test_const_equality_identical_near_zero_values_match() {
    assert!(ast_matches_json(
        &num_node(1e-20),
        &serde_json::json!(1e-20)
    ));
}

#[test]
fn test_const_equality_large_integer_matches_itself() {
    // Large integers must still match exactly.
    let big = 1_000_000_000_000_000f64; // 1e15
    assert!(ast_matches_json(
        &num_node(big),
        &serde_json::json!(1_000_000_000_000_000i64)
    ));
}

#[test]
fn test_const_equality_distinct_large_integers_differ() {
    let a = 1_000_000_000_000_000f64;
    assert!(!ast_matches_json(
        &num_node(a),
        &serde_json::json!(1_000_000_000_000_001i64)
    ));
}

// ===== C22: fractional bounds are rendered as-is in error messages =====

#[test]
fn test_minimum_message_fractional_bound() {
    let v = make_validator();
    let errs = validate_minimum(
        &v,
        &num_node(1.0),
        &serde_json::json!(1.5),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert!(
        errs[0].message.contains("minimum of 1.5"),
        "msg: {}",
        errs[0].message
    );
}

#[test]
fn test_minimum_message_integer_bound_no_decimal() {
    let v = make_validator();
    let errs = validate_minimum(
        &v,
        &num_node(3.0),
        &serde_json::json!(5),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert!(
        errs[0].message.contains("minimum of 5") && !errs[0].message.contains("5.0"),
        "msg: {}",
        errs[0].message
    );
}

#[test]
fn test_maximum_message_fractional_bound() {
    let v = make_validator();
    let errs = validate_maximum(
        &v,
        &num_node(3.0),
        &serde_json::json!(2.5),
        &serde_json::json!({}),
        &[],
    );
    assert_eq!(errs.len(), 1);
    assert!(
        errs[0].message.contains("maximum of 2.5"),
        "msg: {}",
        errs[0].message
    );
}

// ===== C27: cached pattern compilation preserves match semantics =====

#[test]
fn test_pattern_cached_match_and_nonmatch() {
    let v = make_validator();
    let pat = serde_json::json!("^[a-z]+$");
    // Invoke twice to exercise both the compile and cache-hit paths.
    assert!(validate_pattern(&v, &str_node("abc"), &pat, &serde_json::json!({}), &[]).is_empty());
    let errs = validate_pattern(&v, &str_node("ABC"), &pat, &serde_json::json!({}), &[]);
    assert_eq!(errs.len(), 1);
    assert_eq!(errs[0].keyword, "pattern");
    // Second matching call after a cache entry exists still works.
    assert!(validate_pattern(&v, &str_node("xyz"), &pat, &serde_json::json!({}), &[]).is_empty());
}

#[test]
fn test_pattern_invalid_regex_skipped() {
    // A pattern that neither engine can compile yields no error (skipped).
    let v = make_validator();
    let pat = serde_json::json!("[");
    assert!(
        validate_pattern(&v, &str_node("anything"), &pat, &serde_json::json!({}), &[]).is_empty()
    );
}

#[test]
fn test_compile_pattern_cache_returns_consistent_result() {
    // Same pattern compiled twice returns a usable regex both times.
    let re1 = compile_pattern("^foo$").expect("valid");
    assert!(re1.is_match("foo"));
    let re2 = compile_pattern("^foo$").expect("cached");
    assert!(re2.is_match("foo"));
    assert!(!re2.is_match("bar"));
}
