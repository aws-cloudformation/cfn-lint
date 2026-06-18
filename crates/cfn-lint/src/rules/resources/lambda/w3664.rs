crate::extension_schema_rule!(
    W3664,
    id: "W3664",
    description: "Validate Lambda permission Principal matches SourceArn resource type",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::Lambda::Permission",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_permission/permission_principal.json",
    regional: false
);
