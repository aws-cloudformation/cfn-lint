crate::extension_schema_rule!(
    E3676,
    id: "E3676",
    description: "Validate ELBv2 protocols that require certificates have a certificate specified",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElasticLoadBalancingV2::Listener",
    schema_path: "../../../../data/schemas/extensions/aws_elasticloadbalancingv2_listener/certificate.json",
    regional: false
);
