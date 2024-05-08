"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_loadbalancer
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class LoadBalancerApplicationSubnets(CfnLintJsonSchema):
    id = "E3680"
    shortdesc = "Application load balancers require at least 2 subnets"
    description = ""
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ElasticLoadBalancingV2::LoadBalancer/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_loadbalancer,
                filename="application_subnets.json",
            ),
            all_matches=True,
        )
