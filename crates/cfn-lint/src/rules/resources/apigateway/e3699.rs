crate::extension_schema_rule!(
    E3699,
    id: "E3699",
    description: "API Gateway Method and Authorizer must use the same RestApi",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ApiGateway::Method",
    schema_path: "../../../../data/schemas/extensions/aws_apigateway_method/method_authorizer_rest_api.json",
    regional: false
);
