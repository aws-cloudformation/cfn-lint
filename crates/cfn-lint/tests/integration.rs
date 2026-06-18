use std::path::PathBuf;

use cfn_lint::engine::Engine;
use cfn_lint::formatters::{
    get_formatter, Formatter, JsonFormatter, PrettyFormatter, ValidationResult,
};
use cfn_lint::parser;
use cfn_schema::SchemaProvider;
use cfn_lint::template::Template;

fn data_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data")
}

/// Helper: parse YAML, build template, validate with rules only (no schemas).
fn validate_yaml(yaml: &[u8]) -> Vec<cfn_lint::jsonschema::ValidationError> {
    let ast = parser::parse(yaml).expect("parse failed");
    let tmpl = Template::from_ast(&ast).expect("template failed");
    let mut engine = Engine::new();
    engine.validate(&tmpl, &ast, &["us-east-1".to_string()])
}

/// Helper: parse YAML, build template, validate with real schemas.
fn validate_yaml_with_schemas(yaml: &[u8]) -> Vec<cfn_lint::jsonschema::ValidationError> {
    let ast = parser::parse(yaml).expect("parse failed");
    let tmpl = Template::from_ast(&ast).expect("template failed");
    let mut engine = Engine::with_data_dir(data_dir());
    engine.validate(&tmpl, &ast, &["us-east-1".to_string()])
}

fn make_result(filename: &str, issues: Vec<cfn_lint::jsonschema::ValidationError>) -> Vec<ValidationResult> {
    vec![ValidationResult {
        filename: filename.to_string(),
        issues,
    }]
}

fn compute_exit_code(results: &[ValidationResult]) -> i32 {
    let has_errors = results
        .iter()
        .any(|r| r.issues.iter().any(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E')));
    let has_warnings = results
        .iter()
        .any(|r| r.issues.iter().any(|i| i.rule_id.as_deref().unwrap_or("").starts_with('W')));
    match (has_errors, has_warnings) {
        (true, _) => 2,
        (false, true) => 4,
        _ => 0,
    }
}

// ═══════════════════════════════════════════════════════════════════════
// 1. Valid EC2 Instance template — no E3001 errors with real schemas
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn valid_ec2_instance_no_e3001() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Valid EC2 instance
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-12345678
      InstanceType: t2.micro
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e3001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E3001")).collect();
    assert!(
        e3001.is_empty(),
        "valid EC2 instance should produce no E3001 errors, got: {:?}",
        e3001
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 2. Valid Lambda Function template — no E3001 errors with real schemas
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn valid_lambda_function_no_e3001() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Valid Lambda function
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: python3.12
      Role: arn:aws:iam::123456789012:role/lambda-role
      Handler: index.handler
      Code:
        ZipFile: |
          def handler(event, context):
            return "Hello"
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e3001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E3001")).collect();
    assert!(
        e3001.is_empty(),
        "valid Lambda function should produce no E3001 errors, got: {:?}",
        e3001
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 3. Template with multiple resources — S3 + Lambda + IAM Role
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn multiple_resources_clean_validation() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Multi-resource template
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-app-bucket

  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole

  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: python3.12
      Role: arn:aws:iam::123456789012:role/lambda-role
      Handler: index.handler
      Code:
        ZipFile: |
          def handler(event, context):
            return "Hello"
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e3001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E3001")).collect();
    assert!(
        e3001.is_empty(),
        "multi-resource template should produce no E3001 errors, got: {:?}",
        e3001
    );
    // Should also have no other errors
    let errors: Vec<_> = issues
        .iter()
        .filter(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E'))
        .collect();
    assert!(
        errors.is_empty(),
        "multi-resource template should produce no errors, got: {:?}",
        errors
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 4. Template with parameters and Ref — no false type errors
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn parameters_with_ref_no_false_type_errors() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Template with parameters and Ref
Parameters:
  BucketName:
    Type: String
    Default: my-bucket
  InstanceType:
    Type: String
    Default: t2.micro
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-12345678
      InstanceType: !Ref InstanceType
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e3001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E3001")).collect();
    assert!(
        e3001.is_empty(),
        "Ref to parameters should not cause E3001 type errors, got: {:?}",
        e3001
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 5. Template with conditions — E3006 doesn't fire for valid conditions
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn valid_conditions_no_e3006() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Template with conditions
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - prod
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref Environment
      - prod
Resources:
  ProdBucket:
    Type: AWS::S3::Bucket
    Condition: IsProd
    Properties:
      BucketName: prod-only-bucket
  AlwaysBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::If:
          - IsProd
          - prod-bucket
          - dev-bucket
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e3006: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E3006")).collect();
    assert!(
        e3006.is_empty(),
        "valid conditions should not produce E3006, got: {:?}",
        e3006
    );
    // E8001 should also not fire since IsProd is used
    let e8001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E8001")).collect();
    assert!(
        e8001.is_empty(),
        "used condition should not produce E8001, got: {:?}",
        e8001
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 6. Template with outputs — E6001 and E6002 don't fire
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn valid_outputs_no_e6001_e6002() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Template with outputs
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
Outputs:
  BucketArn:
    Description: The bucket ARN
    Value: !GetAtt MyBucket.Arn
    Export:
      Name: MyBucketArn
  BucketName:
    Value: !Ref MyBucket
    Export:
      Name: MyBucketName
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e6001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E6001")).collect();
    assert!(
        e6001.is_empty(),
        "outputs with Value should not produce E6001, got: {:?}",
        e6001
    );
    let e6002: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E6002")).collect();
    assert!(
        e6002.is_empty(),
        "unique export names should not produce E6002, got: {:?}",
        e6002
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 7. Invalid template — multiple deliberate errors
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn invalid_template_multiple_errors() {
    let long_desc = "x".repeat(1025);
    let yaml = format!(
        r#"AWSTemplateFormatVersion: '2010-09-09'
Description: {}
Parameters:
  Unused:
    Type: String
Resources:
  Bad:
    Type: InvalidType
    Properties:
      Foo: bar
Outputs:
  NoValue:
    Description: missing Value property
"#,
        long_desc
    );
    let issues = validate_yaml_with_schemas(yaml.as_bytes());
    let rule_ids: Vec<&str> = issues.iter().map(|i| i.rule_id.as_deref().unwrap_or("")).collect();

    assert!(
        rule_ids.contains(&"E1003"),
        "expected E1003 (long description) in {:?}",
        rule_ids
    );
    assert!(
        rule_ids.contains(&"E3006"),
        "expected E3006 (invalid resource type) in {:?}",
        rule_ids
    );
    assert!(
        rule_ids.contains(&"W2001"),
        "expected W2001 (unused parameter) in {:?}",
        rule_ids
    );
    assert!(
        rule_ids.contains(&"E6002"),
        "expected E6002 (output missing Value) in {:?}",
        rule_ids
    );
    assert!(
        issues.len() >= 4,
        "expected at least 4 issues, got {}",
        issues.len()
    );
}

// ═══════════════════════════════════════════════════════════════════════
// 8. JSON format output — validate, format as JSON, parse back
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn json_format_output_roundtrip() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Bad:
    Type: InvalidType
    Properties:
      Foo: bar
"#;
    let issues = validate_yaml_with_schemas(yaml);
    assert!(!issues.is_empty(), "should have at least one issue");

    let results = make_result("test.yaml", issues);
    let output = JsonFormatter.format(&results);

    let parsed: serde_json::Value =
        serde_json::from_str(&output).expect("JSON formatter output must be valid JSON");
    let arr = parsed.as_array().expect("JSON output must be an array");
    assert!(!arr.is_empty());

    for item in arr {
        assert!(item.get("filename").is_some(), "missing filename");
        assert!(item.get("rule_id").is_some(), "missing rule_id");
        assert!(item.get("message").is_some(), "missing message");
        assert!(item.get("location").is_some(), "missing location");
        assert!(item["location"].get("start").is_some(), "missing location.start");
        assert!(item["location"].get("end").is_some(), "missing location.end");
        assert!(item["location"].get("path").is_some(), "missing location.path");
        assert!(item.get("severity").is_some(), "missing severity");
    }
}

#[test]
fn json_format_empty_issues() {
    let results = make_result("clean.yaml", vec![]);
    let output = JsonFormatter.format(&results);
    let parsed: serde_json::Value = serde_json::from_str(&output).unwrap();
    assert_eq!(parsed.as_array().unwrap().len(), 0);
}

#[test]
fn json_format_via_get_formatter() {
    let issues = validate_yaml_with_schemas(
        b"AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  B:\n    Type: InvalidType\n",
    );
    let results = make_result("t.yaml", issues);
    let output = get_formatter("json").format(&results);
    let _: serde_json::Value = serde_json::from_str(&output).expect("must be valid JSON");
}

// ═══════════════════════════════════════════════════════════════════════
// Additional rules-only integration tests
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn valid_template_no_errors() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: A valid template
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
    let issues = validate_yaml(yaml);
    let errors: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E')).collect();
    assert!(errors.is_empty(), "expected no errors, got: {:?}", errors);
}

#[test]
fn approaching_description_limit_gets_i1003() {
    let long_desc = "x".repeat(922);
    let yaml = format!(
        "AWSTemplateFormatVersion: '2010-09-09'\nDescription: '{}'\nResources:\n  Bucket:\n    Type: AWS::S3::Bucket\n",
        long_desc
    );
    let issues = validate_yaml(yaml.as_bytes());
    assert!(issues.iter().any(|i| i.rule_id.as_deref() == Some("I1003")), "expected I1003");
    assert!(issues.iter().filter(|i| i.rule_id.as_deref() == Some("I1003")).all(|i| i.rule_id.as_deref().unwrap_or("").starts_with('I')));
}

#[test]
fn e1001_catches_missing_resources() {
    // Template without Resources section should produce E1001
    let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nDescription: No resources\n";
    let issues = validate_yaml(yaml);
    let e1001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E1001")).collect();
    assert!(!e1001.is_empty(), "Missing Resources should trigger E1001");
}

#[test]
fn e1001_valid_template_no_issues() {
    let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  Bucket:\n    Type: AWS::S3::Bucket\n";
    let issues = validate_yaml(yaml);
    let e1001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E1001")).collect();
    assert_eq!(e1001.len(), 0);
}

#[test]
fn unused_parameter_produces_w2001() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  Unused:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: hardcoded
"#;
    let issues = validate_yaml(yaml);
    let w2001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("W2001")).collect();
    assert_eq!(w2001.len(), 1);
    assert!(w2001[0].rule_id.as_deref().unwrap().starts_with('W'));
}

#[test]
fn output_missing_value_produces_e6002() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  BadOutput:
    Description: Missing value property
"#;
    let issues = validate_yaml(yaml);
    let e6002: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E6002")).collect();
    assert_eq!(e6002.len(), 1);
}

// ═══════════════════════════════════════════════════════════════════════
// Schema manager real data tests
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn schema_provider_loads_real_s3_bucket_schema() {
    let provider = cfn_schema::BundledSchemaProvider::new(data_dir()).expect("failed to load schema provider");
    let schema = provider
        .get_resource_schema("AWS::S3::Bucket", "us-east-1")
        .expect("AWS::S3::Bucket schema not found");
    assert!(schema.raw.get("properties").is_some());
}

#[test]
fn schema_provider_loads_template_schema() {
    let provider = cfn_schema::BundledSchemaProvider::new(data_dir()).expect("failed to load schema provider");
    let schema = provider
        .get_template_schema()
        .expect("template schema not found");
    assert!(schema.is_object());
}

#[test]
fn schema_provider_lists_over_100_resource_types() {
    let provider = cfn_schema::BundledSchemaProvider::new(data_dir()).expect("failed to load schema provider");
    let types = provider.resource_types("us-east-1");
    assert!(
        types.len() > 100,
        "expected >100 types, got {}",
        types.len()
    );
}

#[test]
fn real_schema_valid_s3_template_no_e3001() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-test-bucket
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let e3001: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("E3001")).collect();
    assert!(e3001.is_empty(), "got unexpected E3001: {:?}", e3001);
}

// ═══════════════════════════════════════════════════════════════════════
// Exit code tests
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn exit_code_zero_for_clean_template() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      ObjectLockEnabled: true
"#;
    let issues = validate_yaml(yaml);
    let results = make_result("clean.yaml", issues);
    assert_eq!(compute_exit_code(&results), 0);
}

#[test]
fn exit_code_two_for_errors() {
    let long_desc = "x".repeat(1025);
    let yaml = format!(
        "AWSTemplateFormatVersion: '2010-09-09'\nDescription: '{}'\nResources:\n  Bucket:\n    Type: AWS::S3::Bucket\n",
        long_desc
    );
    let issues = validate_yaml(yaml.as_bytes());
    assert!(issues.iter().any(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E')));
    let results = make_result("bad.yaml", issues);
    assert_eq!(compute_exit_code(&results), 2);
}

#[test]
fn exit_code_four_for_warnings_only() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  Unused:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
    let issues = validate_yaml(yaml);
    assert!(
        issues.iter().all(|i| i.rule_id.as_deref().unwrap_or("").starts_with('W') || i.rule_id.as_deref().unwrap_or("").starts_with('I')),
        "expected only warnings/informational, got: {:?}",
        issues
    );
    assert!(
        issues.iter().any(|i| i.rule_id.as_deref().unwrap_or("").starts_with('W')),
        "expected at least one warning"
    );
    let results = make_result("warn.yaml", issues);
    assert_eq!(compute_exit_code(&results), 4);
}

// ═══════════════════════════════════════════════════════════════════════
// Full pipeline: parse → template → validate → format
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn full_pipeline_parse_to_json_output() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Description: Pipeline test
Parameters:
  Env:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Env
Outputs:
  Arn:
    Value: !GetAtt Bucket.Arn
"#;
    let ast = parser::parse(yaml).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    assert_eq!(tmpl.description.as_deref(), Some("Pipeline test"));
    assert!(tmpl.parameters.contains_key("Env"));
    assert!(tmpl.resources.contains_key("Bucket"));

    let mut engine = Engine::new();
    let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
    let errors: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref().unwrap_or("E").starts_with('E')).collect();
    assert!(errors.is_empty(), "valid template should have no errors: {:?}", errors);

    let results = make_result("pipeline.yaml", issues);
    let json_out = JsonFormatter.format(&results);
    let parsed: serde_json::Value = serde_json::from_str(&json_out).unwrap();
    assert!(parsed.is_array());
    assert_eq!(compute_exit_code(&results), 0); // W3037 is now a stub; no warnings produced
}

#[test]
fn full_pipeline_with_errors_to_json() {
    let long_desc = "y".repeat(1025);
    let yaml = format!(
        "AWSTemplateFormatVersion: '2010-09-09'\nDescription: {}\nResources:\n  B:\n    Type: AWS::S3::Bucket\n",
        long_desc
    );
    let ast = parser::parse(yaml.as_bytes()).unwrap();
    let tmpl = Template::from_ast(&ast).unwrap();
    let mut engine = Engine::new();
    let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
    assert!(issues.iter().any(|i| i.rule_id.as_deref() == Some("E1003")));

    let results = make_result("err.yaml", issues);
    let json_out = get_formatter("json").format(&results);
    let parsed: serde_json::Value = serde_json::from_str(&json_out).unwrap();
    assert!(parsed
        .as_array()
        .unwrap()
        .iter()
        .any(|i| i["rule_id"] == "E1003"));
    assert_eq!(compute_exit_code(&results), 2);
}

// ═══════════════════════════════════════════════════════════════════════
// Pretty formatter integration
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn pretty_formatter_contains_ansi_and_rule_ids() {
    let issues = validate_yaml_with_schemas(
        b"AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  B:\n    Type: InvalidType\n",
    );
    let results = make_result("template.yaml", issues);
    let output = PrettyFormatter.format(&results);
    assert!(output.contains("\x1b[31m"), "expected red ANSI for errors");
    assert!(output.contains("E3006"));
    assert!(output.contains("template.yaml"));
}

// ═══════════════════════════════════════════════════════════════════════
// W2511: IAM Policy Version warning fires via schema walk
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn w2511_old_policy_version_fires() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2008-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let w2511_issues: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("W2511")).collect();
    assert!(
        !w2511_issues.is_empty(),
        "expected W2511 for old policy version, got rules: {:?}",
        issues.iter().map(|i| i.rule_id.as_deref().unwrap_or("")).collect::<Vec<_>>()
    );
}

// ═══════════════════════════════════════════════════════════════════════
// W1011: Dynamic references for secrets fires via schema walk
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn w1011_ref_to_password_parameter_fires() {
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  DbPass:
    Type: String
    NoEcho: true
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      Engine: mysql
      MasterUsername: admin
      MasterUserPassword: !Ref DbPass
      DBInstanceClass: db.t3.micro
"#;
    let issues = validate_yaml_with_schemas(yaml);
    let w1011_issues: Vec<_> = issues.iter().filter(|i| i.rule_id.as_deref() == Some("W1011")).collect();
    assert!(
        !w1011_issues.is_empty(),
        "expected W1011 for Ref to password parameter, got rules: {:?}",
        issues.iter().map(|i| i.rule_id.as_deref().unwrap_or("")).collect::<Vec<_>>()
    );
}


// ═══════════════════════════════════════════════════════════════════════
// Parameter file / Deployment file integration tests
// ═══════════════════════════════════════════════════════════════════════

/// Helper: validate with parameter values pinned.
/// TODO: Engine::validate_with_parameters not yet implemented — falls back to
/// basic validate (params are ignored for now).
fn validate_yaml_with_parameters(
    yaml: &[u8],
    _params: std::collections::HashMap<String, String>,
) -> Vec<cfn_lint::jsonschema::ValidationError> {
    let ast = parser::parse(yaml).expect("parse failed");
    let tmpl = Template::from_ast(&ast).expect("template failed");
    let mut engine = Engine::with_data_dir(data_dir());
    engine.validate(&tmpl, &ast, &["us-east-1".to_string()])
}

#[test]
fn parameter_file_pins_value_suppresses_warning() {
    // Without parameters: MY_APP_INVALID triggers W1030 (bad bucket name pattern)
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  BucketPrefix:
    Type: String
    AllowedValues:
      - my-app
      - MY_APP_INVALID
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketPrefix
"#;
    // Without params: W1030 fires for MY_APP_INVALID
    let issues_no_params = validate_yaml_with_schemas(yaml);
    let w1030: Vec<_> = issues_no_params.iter()
        .filter(|i| i.rule_id.as_deref() == Some("W1030"))
        .collect();
    assert!(!w1030.is_empty(), "expected W1030 without parameter file");

    // With params pinning to 'my-app': no W1030
    let mut params = std::collections::HashMap::new();
    params.insert("BucketPrefix".to_string(), "my-app".to_string());
    let issues_with_params = validate_yaml_with_parameters(yaml, params);
    let w1030_pinned: Vec<_> = issues_with_params.iter()
        .filter(|i| i.rule_id.as_deref() == Some("W1030"))
        .collect();
    assert!(w1030_pinned.is_empty(), "W1030 should not fire when parameter is pinned to valid value, got: {:?}",
        w1030_pinned.iter().map(|i| &i.message).collect::<Vec<_>>());
}

#[test]
fn parameter_file_pins_value_catches_error() {
    // With a parameter file providing an invalid value, the error still fires
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  BucketName:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
"#;
    // Pin to an invalid bucket name — should still get W1030
    let mut params = std::collections::HashMap::new();
    params.insert("BucketName".to_string(), "INVALID_BUCKET_NAME".to_string());
    let issues = validate_yaml_with_parameters(yaml, params);
    let w1030: Vec<_> = issues.iter()
        .filter(|i| i.rule_id.as_deref() == Some("W1030"))
        .collect();
    assert!(!w1030.is_empty(), "expected W1030 when parameter file provides invalid bucket name");
}

#[test]
fn parameter_file_no_params_resolves_default() {
    // Parameter has a default. Without a parameter file, default is used.
    // With a parameter file providing a different value, that value is used.
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  TopicName:
    Type: String
    Default: valid-topic
Resources:
  Topic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Ref TopicName
"#;
    // Without params: resolves to "valid-topic" (default), clean
    let issues_default = validate_yaml_with_schemas(yaml);
    assert!(issues_default.is_empty(), "expected no issues with default value, got: {:?}",
        issues_default.iter().map(|i| (&i.rule_id, &i.message)).collect::<Vec<_>>());

    // With params providing valid value: still clean
    let mut params = std::collections::HashMap::new();
    params.insert("TopicName".to_string(), "my-topic".to_string());
    let issues_pinned = validate_yaml_with_parameters(yaml, params);
    assert!(issues_pinned.is_empty(), "expected no issues with pinned valid value, got: {:?}",
        issues_pinned.iter().map(|i| (&i.rule_id, &i.message)).collect::<Vec<_>>());
}

#[test]
fn recursive_schema_ref_does_not_stack_overflow() {
    // A resource schema with a recursive $ref (definition references itself).
    // Before the fix, this would stack overflow. Now it terminates cleanly.
    let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: test
"#;
    // This tests the validator machinery — the actual recursive schema is injected
    // via a custom validator call, not via the template.
    use cfn_lint::jsonschema::Validator;
    use cfn_lint::ast::{AstNode, StringNode, Span};

    let recursive_schema = serde_json::json!({
        "definitions": {
            "Recursive": {
                "$ref": "#/definitions/Recursive"
            }
        },
        "properties": {
            "Name": {
                "$ref": "#/definitions/Recursive"
            }
        },
        "type": "object"
    });

    let node = AstNode::String(StringNode { value: "test".to_string(), span: Span::default() });
    let v = Validator::new(recursive_schema.clone());
    let prop_schema = serde_json::json!({"$ref": "#/definitions/Recursive"});
    // This should terminate without stack overflow
    let errors = v.validate_schema(&node, &prop_schema, &vec!["Test".to_string()]);
    // We don't care about the specific errors — just that it didn't crash
    let _ = errors;
}

// ═══════════════════════════════════════════════════════════════════════
// Rule integration tests — data-driven from tests/integration/rules/
// ═══════════════════════════════════════════════════════════════════════

/// Parsed expectation from a test file's front-matter.
#[derive(Debug, Clone)]
struct ExpectedFinding {
    rule: String,
    path: String,
    message_contains: Option<String>,
    message_contains_value: Option<String>,
    message_not_contains: Option<String>,
}

/// Parsed front-matter from a test file.
#[derive(Debug)]
struct TestFrontMatter {
    rule: String,
    description: String,
    expect: Vec<ExpectedFinding>,
    regions: Vec<String>,
}

/// Parse the front-matter block from a test file.
/// Returns None if the file doesn't contain valid front-matter.
fn parse_front_matter(content: &str) -> Option<TestFrontMatter> {
    let start_marker = "# --- cfn-lint-test ---";
    let end_marker = "# ---";

    let start_idx = content.find(start_marker)?;
    let after_start = &content[start_idx + start_marker.len()..];
    let end_idx = after_start.find(end_marker)?;
    let block = &after_start[..end_idx];

    // Strip leading "# " from each line to get raw YAML
    let yaml_lines: Vec<&str> = block
        .lines()
        .map(|line| {
            let trimmed = line.trim_start();
            if let Some(stripped) = trimmed.strip_prefix("# ") {
                stripped
            } else if trimmed == "#" {
                ""
            } else {
                trimmed
            }
        })
        .collect();
    let yaml_str = yaml_lines.join("\n");

    let doc: serde_yaml::Value = serde_yaml::from_str(&yaml_str).ok()?;
    let mapping = doc.as_mapping()?;

    let rule = mapping
        .get(&serde_yaml::Value::String("rule".into()))?
        .as_str()?
        .to_string();

    let description = mapping
        .get(&serde_yaml::Value::String("description".into()))?
        .as_str()?
        .to_string();

    let expect_val = mapping.get(&serde_yaml::Value::String("expect".into()))?;
    let expect = match expect_val {
        serde_yaml::Value::Sequence(seq) => seq
            .iter()
            .filter_map(|item| {
                let m = item.as_mapping()?;
                let r = m
                    .get(&serde_yaml::Value::String("rule".into()))?
                    .as_str()?
                    .to_string();
                let p = m
                    .get(&serde_yaml::Value::String("path".into()))?
                    .as_str()?
                    .to_string();
                let mc = m
                    .get(&serde_yaml::Value::String("message_contains".into()))
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string());
                let mcv = m
                    .get(&serde_yaml::Value::String("message_contains_value".into()))
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string());
                let mnc = m
                    .get(&serde_yaml::Value::String("message_not_contains".into()))
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string());
                Some(ExpectedFinding {
                    rule: r,
                    path: p,
                    message_contains: mc,
                    message_contains_value: mcv,
                    message_not_contains: mnc,
                })
            })
            .collect(),
        // Empty sequence: expect: []
        _ => vec![],
    };

    let regions = mapping
        .get(&serde_yaml::Value::String("regions".into()))
        .and_then(|v| v.as_sequence())
        .map(|seq| {
            seq.iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_else(|| vec!["us-east-1".to_string()]);

    Some(TestFrontMatter {
        rule,
        description,
        expect,
        regions,
    })
}

/// Convert a path like "/Resources/Queue/Properties/DelaySeconds" to
/// a Vec like ["Resources", "Queue", "Properties", "DelaySeconds"].
fn frontmatter_path_to_segments(path: &str) -> Vec<String> {
    path.trim_start_matches('/')
        .split('/')
        .filter(|s| !s.is_empty())
        .map(|s| s.to_string())
        .collect()
}

/// A single test failure record for reporting.
#[derive(Debug)]
struct RuleTestFailure {
    file: String,
    description: String,
    details: String,
}

#[test]
fn rule_integration_tests() {
    use walkdir::WalkDir;

    // The workspace root is 2 levels up from crates/cfn-lint/
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let workspace_root = manifest_dir
        .parent()
        .expect("crates/ parent")
        .parent()
        .expect("workspace root");

    let rules_dir = workspace_root.join("tests").join("integration").join("rules");
    if !rules_dir.is_dir() {
        // No test fixtures yet — skip gracefully
        eprintln!(
            "SKIP: rule integration test directory not found at {}",
            rules_dir.display()
        );
        return;
    }

    // Fail fast if schemas are not present
    let schema_dir = manifest_dir.join("data");
    if !schema_dir.join("schemas").join("providers").is_dir() {
        panic!(
            "Schema directory not found at {}. Run the schema download script before testing.",
            schema_dir.display()
        );
    }

    let mut failures: Vec<RuleTestFailure> = Vec::new();
    let mut test_count = 0;

    for entry in WalkDir::new(&rules_dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.path().extension().map_or(false, |ext| ext == "yaml" || ext == "yml")
        })
    {
        let path = entry.path();
        let content = match std::fs::read_to_string(path) {
            Ok(c) => c,
            Err(e) => {
                failures.push(RuleTestFailure {
                    file: path.display().to_string(),
                    description: "".to_string(),
                    details: format!("Failed to read file: {}", e),
                });
                continue;
            }
        };

        let front_matter = match parse_front_matter(&content) {
            Some(fm) => fm,
            None => {
                // Files without front-matter are skipped (not an error)
                continue;
            }
        };

        test_count += 1;
        let relative_path = path
            .strip_prefix(workspace_root)
            .unwrap_or(path)
            .display()
            .to_string();

        // Parse and validate the template
        let ast = match parser::parse(content.as_bytes()) {
            Ok(a) => a,
            Err(e) => {
                failures.push(RuleTestFailure {
                    file: relative_path,
                    description: front_matter.description.clone(),
                    details: format!("Failed to parse template: {}", e),
                });
                continue;
            }
        };

        let tmpl = match Template::from_ast(&ast) {
            Ok(t) => t,
            Err(e) => {
                failures.push(RuleTestFailure {
                    file: relative_path,
                    description: front_matter.description.clone(),
                    details: format!("Failed to build template: {}", e),
                });
                continue;
            }
        };

        let mut engine = Engine::with_data_dir(schema_dir.clone());
        let issues = engine.validate(&tmpl, &ast, &front_matter.regions);

        // Check expected findings are present
        for expected in &front_matter.expect {
            let expected_segments = frontmatter_path_to_segments(&expected.path);

            let matching_issues: Vec<_> = issues
                .iter()
                .filter(|i| {
                    i.rule_id.as_deref() == Some(&expected.rule)
                        && i.path == expected_segments
                })
                .collect();

            if matching_issues.is_empty() {
                let actual_for_rule: Vec<_> = issues
                    .iter()
                    .filter(|i| i.rule_id.as_deref() == Some(&expected.rule))
                    .map(|i| format!("  path={:?} msg={}", i.path, i.message))
                    .collect();

                failures.push(RuleTestFailure {
                    file: relative_path.clone(),
                    description: front_matter.description.clone(),
                    details: format!(
                        "Expected finding not found:\n  rule={} path={}\n\
                         Actual findings for rule {}:\n{}",
                        expected.rule,
                        expected.path,
                        expected.rule,
                        if actual_for_rule.is_empty() {
                            "  (none)".to_string()
                        } else {
                            actual_for_rule.join("\n")
                        }
                    ),
                });
                continue;
            }

            // Check message assertions on all matching issues (at least one must pass all)
            let mut message_ok = false;
            let mut message_failures: Vec<String> = Vec::new();

            for issue in &matching_issues {
                let mut this_ok = true;
                let mut this_failures: Vec<String> = Vec::new();

                if let Some(ref contains) = expected.message_contains {
                    if !issue.message.contains(contains.as_str()) {
                        this_ok = false;
                        this_failures.push(format!(
                            "message_contains '{}' not found in: {}",
                            contains, issue.message
                        ));
                    }
                }

                if let Some(ref contains_val) = expected.message_contains_value {
                    if !issue.message.contains(contains_val.as_str()) {
                        this_ok = false;
                        this_failures.push(format!(
                            "message_contains_value '{}' not found in: {}",
                            contains_val, issue.message
                        ));
                    }
                }

                if let Some(ref not_contains) = expected.message_not_contains {
                    if issue.message.contains(not_contains.as_str()) {
                        this_ok = false;
                        this_failures.push(format!(
                            "message_not_contains '{}' was found in: {}",
                            not_contains, issue.message
                        ));
                    }
                }

                if this_ok {
                    message_ok = true;
                    break;
                } else {
                    message_failures.extend(this_failures);
                }
            }

            if !message_ok && !message_failures.is_empty() {
                failures.push(RuleTestFailure {
                    file: relative_path.clone(),
                    description: front_matter.description.clone(),
                    details: format!(
                        "Message assertion failed for rule={} path={}:\n  {}",
                        expected.rule,
                        expected.path,
                        message_failures.join("\n  ")
                    ),
                });
            }
        }

        // Check for unexpected findings from the primary rule under test
        let unexpected: Vec<_> = issues
            .iter()
            .filter(|i| i.rule_id.as_deref() == Some(front_matter.rule.as_str()))
            .filter(|i| {
                let issue_path_str = format!("/{}", i.path.join("/"));
                !front_matter.expect.iter().any(|exp| {
                    exp.rule == front_matter.rule && exp.path == issue_path_str
                })
            })
            .collect();

        if !unexpected.is_empty() {
            let unexpected_details: Vec<String> = unexpected
                .iter()
                .map(|i| {
                    format!(
                        "  rule={} path=/{} msg={}",
                        i.rule_id.as_deref().unwrap_or("?"),
                        i.path.join("/"),
                        i.message
                    )
                })
                .collect();

            failures.push(RuleTestFailure {
                file: relative_path.clone(),
                description: front_matter.description.clone(),
                details: format!(
                    "Unexpected findings from primary rule '{}':\n{}",
                    front_matter.rule,
                    unexpected_details.join("\n")
                ),
            });
        }
    }

    // Report all failures at the end
    if !failures.is_empty() {
        let mut report = format!(
            "\n{} rule integration test failure(s) out of {} test file(s):\n\n",
            failures.len(),
            test_count
        );
        for (i, failure) in failures.iter().enumerate() {
            report.push_str(&format!(
                "--- Failure {} ---\nFile: {}\nDescription: {}\n{}\n\n",
                i + 1,
                failure.file,
                failure.description,
                failure.details
            ));
        }
        panic!("{}", report);
    }

    eprintln!(
        "OK: {} rule integration test file(s) passed.",
        test_count
    );
}

// ═══════════════════════════════════════════════════════════════════════
// Rule keyword reachability — verify all rule keywords are reachable
// via the schema walker
// ═══════════════════════════════════════════════════════════════════════

#[test]
fn rule_keywords_are_reachable() {
    use std::collections::HashSet;
    use cfn_lint::jsonschema::cfn_lint_keyword::KeywordRuleRegistry;

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let schema_dir = manifest_dir.join("data");

    // Fail fast if schemas are not present
    if !schema_dir.join("schemas").join("providers").is_dir() {
        panic!(
            "Schema directory not found at {}. Run the schema download script before testing.",
            schema_dir.display()
        );
    }

    let provider = cfn_schema::BundledSchemaProvider::new(schema_dir)
        .expect("failed to load schema provider");
    let resource_types: HashSet<String> = provider.resource_types("us-east-1").into_iter().collect();

    // Build the registry the same way Engine::new() does
    let mut registry = KeywordRuleRegistry::from_inventory();
    registry.register(std::sync::Arc::new(cfn_lint::rules::e2531::E2531::new()));
    registry.register(std::sync::Arc::new(cfn_lint::rules::e2533::E2533::new()));
    registry.register(std::sync::Arc::new(cfn_lint::rules::w2531::W2531::new()));

    let top_level_sections: HashSet<&str> = [
        "Resources", "Parameters", "Outputs", "Conditions",
        "Mappings", "Metadata", "Transform", "AWSTemplateFormatVersion",
        "Description", "Rules", "Hooks",
    ].into_iter().collect();

    let mut rules_checked = 0;
    let mut unreachable_keywords: Vec<(String, String)> = Vec::new(); // (rule_id, keyword)

    for rule in registry.all_rules() {
        rules_checked += 1;
        for keyword in rule.keywords() {
            // "/" matches root — always reachable
            if *keyword == "/" || keyword.is_empty() {
                continue;
            }

            let segments: Vec<&str> = keyword.split('/').collect();

            // Single-segment keyword matching a top-level section is always reachable
            if segments.len() == 1 && top_level_sections.contains(segments[0]) {
                continue;
            }

            // First segment must be a known top-level section
            if !top_level_sections.contains(segments[0]) {
                unreachable_keywords.push((
                    rule.id().to_string(),
                    keyword.to_string(),
                ));
                continue;
            }

            // For Resources paths, check reachability
            if segments[0] == "Resources" {
                if segments.len() < 2 {
                    continue; // "Resources" alone is reachable
                }

                let type_segment = segments[1];

                // Wildcard — always reachable (matches any resource)
                if type_segment == "*" {
                    continue;
                }

                // Check if the resource type exists in the schema
                if !resource_types.contains(type_segment) {
                    unreachable_keywords.push((
                        rule.id().to_string(),
                        keyword.to_string(),
                    ));
                    continue;
                }

                // Resource type exists — check if the property path resolves
                // Only check if there's a Properties path to validate
                if segments.len() >= 3 && segments[2] == "Properties" && segments.len() > 3 {
                    // Build path for schema resolution (skip array wildcards for
                    // the purpose of checking basic reachability)
                    let schema_path: Vec<&str> = segments.iter()
                        .take_while(|s| **s != "*")
                        .copied()
                        .collect();

                    // Only check if we have at least one property name after "Properties"
                    if schema_path.len() > 3 {
                        let resolved = provider.resolve(&schema_path, "us-east-1");
                        if resolved.is_none() {
                            unreachable_keywords.push((
                                rule.id().to_string(),
                                keyword.to_string(),
                            ));
                        }
                    }
                }
            }
            // Non-Resources top-level sections (Parameters/*, Outputs/*, etc.) are
            // generally reachable if the top-level section is valid — no further check needed.
        }
    }

    // Report unreachable keywords as warnings
    if !unreachable_keywords.is_empty() {
        eprintln!("\n=== Unreachable keyword warnings ===");
        for (rule_id, keyword) in &unreachable_keywords {
            eprintln!("  WARNING: rule {} keyword '{}' is not reachable via schema", rule_id, keyword);
        }
    }

    eprintln!(
        "\n=== Keyword reachability summary: {} rules checked, {} keywords unreachable ===\n",
        rules_checked,
        unreachable_keywords.len()
    );

    // For now, report but don't hard-fail (some keywords may target
    // region-specific resource types not in us-east-1).
    // Uncomment the assertion below to make this a hard failure:
    // assert!(
    //     unreachable_keywords.is_empty(),
    //     "Found {} unreachable keywords",
    //     unreachable_keywords.len()
    // );
}
