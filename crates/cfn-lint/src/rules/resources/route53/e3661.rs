crate::extension_schema_rule!(
    E3661,
    id: "E3661",
    description: "Validate Route53 health check has AlarmIdentifier when using CloudWatch",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Route53::HealthCheck",
    schema_path: "../../../../data/schemas/extensions/aws_route53_healthcheck/healthcheckconfig_type_inclusive.json",
    regional: false,
    property: "HealthCheckConfig"
);
