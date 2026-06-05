"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_sagemaker_cluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class ClusterInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3644"
    shortdesc = "Validate SageMaker cluster instance types based on region"
    description = (
        "Validates the SageMaker cluster instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::SageMaker::Cluster/Properties/InstanceGroups/*/InstanceType",
                "Resources/AWS::SageMaker::Cluster/Properties/RestrictedInstanceGroups/*/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sagemaker_cluster,
                filename="instancetype_enum.json",
            ),
        )
