"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticsearch_domain
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DomainClusterConfigInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3652"
    shortdesc = "Validate Elasticsearch domain cluster instance"
    description = (
        "Validates the Elasticsearch instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Elasticsearch::Domain/Properties/ElasticsearchClusterConfig/InstanceType"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticsearch_domain,
                filename="elasticsearchclusterconfig_instancetype_enum.json",
            ),
        )
