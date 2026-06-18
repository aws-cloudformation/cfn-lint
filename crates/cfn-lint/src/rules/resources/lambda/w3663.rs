crate::extension_schema_rule!(
    W3663,
    id: "W3663",
    description: "Validate SourceAccount is required property",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::Lambda::Permission",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_permission/permission_source_account.json",
    regional: false
);
