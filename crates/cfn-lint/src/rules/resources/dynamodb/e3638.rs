crate::extension_schema_rule!(
    E3638,
    id: "E3638",
    description: "Validate DynamoDB BillingMode pay per request configuration",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::DynamoDB::Table",
    schema_path: "../../../../data/schemas/extensions/aws_dynamodb_table/billingmode_exclusive.json",
    regional: false
);
