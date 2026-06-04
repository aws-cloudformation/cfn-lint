"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_sagemaker_processing
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class ProcessingInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3640"
    shortdesc = "Validate SageMaker processing instance types based on region"
    description = (
        "Validates the SageMaker processing instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::SageMaker::DataQualityJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
                "Resources/AWS::SageMaker::ModelBiasJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
                "Resources/AWS::SageMaker::ModelExplainabilityJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
                "Resources/AWS::SageMaker::ModelQualityJobDefinition/Properties/JobResources/ClusterConfig/InstanceType",
                "Resources/AWS::SageMaker::MonitoringSchedule/Properties/MonitoringScheduleConfig/MonitoringJobDefinition/MonitoringResources/ClusterConfig/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sagemaker_processing,
                filename="instancetype_enum.json",
            ),
        )
