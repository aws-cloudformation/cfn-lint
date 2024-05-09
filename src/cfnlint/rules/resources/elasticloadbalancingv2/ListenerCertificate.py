"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_listener
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ListenerCertificate(CfnLintJsonSchema):
    id = "E3676"
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
                "Resources/AWS::ElasticLoadBalancingV2::Listener/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_listener,
                filename="certificate.json",
            ),
            all_matches=True,
        )
