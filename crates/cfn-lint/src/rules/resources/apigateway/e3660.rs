crate::extension_schema_rule!(
    E3660,
    id: "E3660",
    description: "RestApi requires a name when not using an OpenAPI specification",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ApiGateway::RestApi",
    schema_path: "../../../../data/schemas/extensions/aws_apigateway_restapi/openapi_properties.json",
    regional: false
);
