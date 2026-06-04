"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_sagemaker_transform
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class TransformInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3643"
    shortdesc = "Validate SageMaker transform instance types based on region"
    description = (
        "Validates the SageMaker transform instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::SageMaker::ModelPackage/Properties/ValidationSpecification/ValidationProfiles/*/TransformJobDefinition/TransformResources/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sagemaker_transform,
                filename="instancetype_enum.json",
            ),
        )
