"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_sagemaker_hosting
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class HostingInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3642"
    shortdesc = "Validate SageMaker hosting instance types based on region"
    description = (
        "Validates the SageMaker hosting/inference instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::SageMaker::InferenceExperiment/Properties/ModelVariants/*/InfrastructureConfig/RealTimeInferenceConfig/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sagemaker_hosting,
                filename="instancetype_enum.json",
            ),
        )
