crate::extension_schema_rule!(
    E3054,
    id: "E3054",
    description: "Validate ECS service using Fargate uses TaskDefinition that allows Fargate",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ECS::Service",
    schema_path: "../../../../data/schemas/extensions/aws_ecs_service/service_fargate.json",
    regional: false
);
