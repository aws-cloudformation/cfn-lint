crate::extension_schema_rule!(
    E3044,
    id: "E3044",
    description: "ECS service using FARGATE or EXTERNAL can only use SchedulingStrategy of REPLICA",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ECS::Service",
    schema_path: "../../../../data/schemas/extensions/aws_ecs_service/fargate.json",
    regional: false
);
