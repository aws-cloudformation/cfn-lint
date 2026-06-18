crate::extension_schema_rule!(
    E3683,
    id: "E3683",
    description: "Validate target group protocol property restrictions",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElasticLoadBalancingV2::TargetGroup",
    schema_path: "../../../../data/schemas/extensions/aws_elasticloadbalancingv2_targetgroup/protocol_restrictions.json",
    regional: false
);
