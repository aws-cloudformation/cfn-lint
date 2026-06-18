crate::extension_schema_rule!(
    E3698,
    id: "E3698",
    description: "API Gateway Stage and Deployment must use the same RestApi",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ApiGateway::Stage",
    schema_path: "../../../../data/schemas/extensions/aws_apigateway_stage/stage_deployment_rest_api.json",
    regional: false
);
