crate::extension_schema_rule!(
    E3696,
    id: "E3696",
    description: "LogLevel is not supported when LogFormat is set to Text",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::Function",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_function/loglevel_logformat.json",
    regional: false
);
