crate::extension_schema_rule!(
    E3678,
    id: "E3678",
    description: "Using the ZipFile attribute requires a runtime to be specified",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::Function",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_function/zipfile_runtime_exists.json",
    regional: false
);
