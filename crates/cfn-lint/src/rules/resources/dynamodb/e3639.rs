crate::extension_schema_rule!(
    E3639,
    id: "E3639",
    description: "When BillingMode is Provisioned you must specify ProvisionedThroughput",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::DynamoDB::Table",
    schema_path: "../../../../data/schemas/extensions/aws_dynamodb_table/billingmode_provisioned_dependent.json",
    regional: false
);
