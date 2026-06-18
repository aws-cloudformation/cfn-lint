crate::extension_schema_rule!(
    W3694,
    id: "W3694",
    description: "SNS Subscription Endpoint should match Protocol",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::SNS::Subscription",
    schema_path: "../../../../data/schemas/extensions/aws_sns_subscription/subscription_endpoint_protocol.json",
    regional: false
);
