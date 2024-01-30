"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DomainClusterConfigInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3652"
    shortdesc = "Validate Elasticsearch domain cluster instance"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            ["aws_elasticsearch_domain/elasticsearchclusterconfig_instancetype_enum"]
        )
