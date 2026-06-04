"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_sagemaker_training
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class TrainingInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3645"
    shortdesc = "Validate SageMaker training instance types based on region"
    description = (
        "Validates the SageMaker training instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::SageMaker::TrainingJob/Properties/ResourceConfig/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sagemaker_training,
                filename="instancetype_enum.json",
            ),
        )
