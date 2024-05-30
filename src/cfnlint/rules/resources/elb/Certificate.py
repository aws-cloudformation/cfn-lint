"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticloadbalancing_loadbalancer
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Certificate(CfnLintJsonSchema):
    id = "E3679"
    shortdesc = (
        "Validate ELB protocols that require certificates have a certificate specified"
    )
    description = "When using HTTPS or SSL you must provide a certificate"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-elasticloadbalancing-loadbalancer-listeners.html#cfn-elasticloadbalancing-loadbalancer-listeners-sslcertificateid"
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
