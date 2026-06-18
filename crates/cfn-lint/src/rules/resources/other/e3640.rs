crate::extension_schema_rule!(
    E3640,
    id: "E3640",
    description: "Validate SageMaker processing instance types based on region",
    severity: crate::rules::Severity::Error,
    schema_path: "../../../../data/schemas/extensions/aws_sagemaker_processing/instancetype_enum.json",
    keywords: [
        "Resources/AWS::SageMaker::DataQualityJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
        "Resources/AWS::SageMaker::ModelBiasJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
        "Resources/AWS::SageMaker::ModelExplainabilityJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
        "Resources/AWS::SageMaker::ModelQualityJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
        "Resources/AWS::SageMaker::MonitoringSchedule/Properties/MonitoringScheduleConfig/MonitoringJobDefinition/MonitoringResources/ClusterConfig/InstanceType",
    ]
);
