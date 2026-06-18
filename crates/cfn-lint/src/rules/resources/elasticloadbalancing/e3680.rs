crate::extension_schema_rule!(
    E3680,
    id: "E3680",
    description: "Application load balancers require at least 2 subnets",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElasticLoadBalancingV2::LoadBalancer",
    schema_path: "../../../../data/schemas/extensions/aws_elasticloadbalancingv2_loadbalancer/application_subnets.json",
    regional: false
);
