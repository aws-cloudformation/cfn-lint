crate::extension_schema_rule!(
    E3711,
    id: "E3711",
    description: "Validate ListenerRule target group protocol is not GENEVE",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElasticLoadBalancingV2::ListenerRule",
    schema_path: "../../../../data/schemas/extensions/aws_elasticloadbalancingv2_listenerrule/listener_rule_target_group_protocol.json",
    regional: false
);
