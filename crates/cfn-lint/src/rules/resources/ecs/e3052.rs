crate::extension_schema_rule!(
    E3052,
    id: "E3052",
    description: "Validate ECS service requires NetworkConfiguration",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ECS::Service",
    schema_path: "../../../../data/schemas/extensions/aws_ecs_service/service_network_configuration.json",
    regional: false
);
