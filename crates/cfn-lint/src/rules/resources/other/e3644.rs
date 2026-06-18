crate::extension_schema_rule!(
    E3644,
    id: "E3644",
    description: "Validate SageMaker cluster instance types based on region",
    severity: crate::rules::Severity::Error,
    schema_path: "../../../../data/schemas/extensions/aws_sagemaker_cluster/instancetype_enum.json",
    keywords: [
        "Resources/AWS::SageMaker::Cluster/Properties/InstanceGroups/*/InstanceType",
        "Resources/AWS::SageMaker::Cluster/Properties/RestrictedInstanceGroups/*/InstanceType",
    ]
);
