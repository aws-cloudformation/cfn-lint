crate::extension_schema_rule!(
    E3047,
    id: "E3047",
    description: "Validate ECS Fargate tasks have the right combination of CPU and memory",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ECS::TaskDefinition",
    schema_path: "../../../../data/schemas/extensions/aws_ecs_taskdefinition/fargate_cpu_memory.json",
    regional: false
);
