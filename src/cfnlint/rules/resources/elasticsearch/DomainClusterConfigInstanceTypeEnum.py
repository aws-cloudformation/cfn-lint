"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class DomainClusterConfigInstanceTypeEnum(BaseCfnRegionSchema):
    id = "E3652"
    shortdesc = "Validate Elasticsearch domain cluster instance"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = (
        "aws_elasticsearch_domain/elasticsearchclusterconfig_instancetype_enum"
    )
