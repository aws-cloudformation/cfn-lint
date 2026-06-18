crate::extension_schema_rule!(
    E3663,
    id: "E3663",
    description: "Validate Lambda environment variable names are not reserved",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::Function",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_function/environment_variable_keys.json",
    regional: false,
    property: "Environment/Variables"
);
