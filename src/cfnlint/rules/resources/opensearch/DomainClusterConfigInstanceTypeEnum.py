"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_opensearchservice_domain
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DomainClusterConfigInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3653"
    shortdesc = "Validate OpenSearch domain cluster instance type"
    description = (
        "Validates the OpenSearch instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::OpenSearchService::Domain/Properties/ClusterConfig/InstanceType"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_opensearchservice_domain,
                filename="clusterconfig_instancetype_enum.json",
            ),
        )
