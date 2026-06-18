crate::extension_schema_rule!(
    E3642,
    id: "E3642",
    description: "Validate SageMaker hosting instance types based on region",
    severity: crate::rules::Severity::Error,
    schema_path: "../../../../data/schemas/extensions/aws_sagemaker_hosting/instancetype_enum.json",
    keywords: [
        "Resources/AWS::SageMaker::InferenceExperiment/Properties/ModelVariants/*/InfrastructureConfig/RealTimeInferenceConfig/InstanceType",
    ]
);
