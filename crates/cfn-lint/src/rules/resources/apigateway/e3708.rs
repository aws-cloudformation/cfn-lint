crate::extension_schema_rule!(
    E3708,
    id: "E3708",
    description: "API Gateway AuthorizationType must match Authorizer Type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ApiGateway::Method",
    schema_path: "../../../../data/schemas/extensions/aws_apigateway_method/method_authorizer_type.json",
    regional: false
);
