crate::extension_schema_rule!(
    E3643,
    id: "E3643",
    description: "Validate SageMaker transform instance types based on region",
    severity: crate::rules::Severity::Error,
    schema_path: "../../../../data/schemas/extensions/aws_sagemaker_transform/instancetype_enum.json",
    keywords: [
        "Resources/AWS::SageMaker::ModelPackage/Properties/ValidationSpecification/ValidationProfiles/*/TransformJobDefinition/TransformResources/InstanceType",
    ]
);
