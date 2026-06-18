crate::extension_schema_rule!(
    E3684,
    id: "E3684",
    description: "Validate target group health check protocol property restrictions",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElasticLoadBalancingV2::TargetGroup",
    schema_path: "../../../../data/schemas/extensions/aws_elasticloadbalancingv2_targetgroup/healthcheckprotocol_restrictions.json",
    regional: false
);
