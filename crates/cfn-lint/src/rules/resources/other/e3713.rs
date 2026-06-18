crate::extension_schema_rule!(
    E3713,
    id: "E3713",
    description: "Validate Fargate ECS services use supported log drivers",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ECS::Service",
    schema_path: "../../../../data/schemas/extensions/aws_ecs_service/service_fargate_log_driver.json",
    regional: false
);
