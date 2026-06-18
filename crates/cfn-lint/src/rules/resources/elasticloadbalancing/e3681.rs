crate::extension_schema_rule!(
    E3681,
    id: "E3681",
    description: "Validate target group target type property restrictions",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElasticLoadBalancingV2::TargetGroup",
    schema_path: "../../../../data/schemas/extensions/aws_elasticloadbalancingv2_targetgroup/targettype_restrictions.json",
    regional: false
);
