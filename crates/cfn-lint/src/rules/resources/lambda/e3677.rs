crate::extension_schema_rule!(
    E3677,
    id: "E3677",
    description: "Validate Lambda using ZipFile requires an allowable runtime",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::Function",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_function/zipfile_runtime_enum.json",
    regional: false
);
