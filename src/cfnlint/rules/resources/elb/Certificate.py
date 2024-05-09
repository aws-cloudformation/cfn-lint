"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticloadbalancing_loadbalancer
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Certificate(CfnLintJsonSchema):
    id = "E3679"
    shortdesc = (
        "Validate protocols that require certificates have a certificate specified"
    )
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ElasticLoadBalancing::LoadBalancer/Properties/Listeners/*",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticloadbalancing_loadbalancer,
                filename="certificate.json",
            ),
            all_matches=True,
        )
