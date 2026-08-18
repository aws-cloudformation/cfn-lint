crate::extension_schema_rule!(
    E3685,
    id: "E3685",
    description: "Container image functions cannot use Handler, Runtime, or Layers",
    severity: crate::rules::Severity::Error,
    schema_path: "../../../../data/schemas/extensions/aws_lambda_function/packagetype_image_exclusions.json",
    regional: false,
    keywords: [
        "Resources/AWS::Lambda::Function/Properties",
        "Resources/AWS::Serverless::Function/Properties",
    ]
);
