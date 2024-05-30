"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_listener
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ListenerCertificate(CfnLintJsonSchema):
    id = "E3676"
    shortdesc = (
        "Validate ELBv2 protocols that require certificates "
        "have a certificate specified"
    )
    description = "When using HTTP or TLS you must specify a certificate"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticloadbalancingv2-listener.html#cfn-elasticloadbalancingv2-listener-certificates"
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
