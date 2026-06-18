crate::extension_schema_rule!(
    E3718,
    id: "E3718",
    description: "Validate API Gateway Authorizer TTL based on type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ApiGateway::Authorizer",
    schema_path: "../../../../data/schemas/extensions/aws_apigateway_authorizer/ttl.json",
    regional: false
);
