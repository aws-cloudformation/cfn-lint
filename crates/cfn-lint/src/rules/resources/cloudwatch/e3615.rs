crate::extension_schema_rule!(
    E3615,
    id: "E3615",
    description: "Validate the period is a valid value",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::CloudWatch::Alarm",
    schema_path: "../../../../data/schemas/extensions/aws_cloudwatch_alarm/period.json",
    regional: false
);
