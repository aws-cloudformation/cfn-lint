"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_route53_recordset
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class RecordSet(CfnLintJsonSchema):
    """Check Route53 Recordset Configuration"""

    id = "E3023"
    shortdesc = "Validate Route53 RecordSets"
    description = "Check if all RecordSets are correctly configured"
    source_url = "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html"
    tags = ["resources", "route53", "record_set"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Route53::RecordSet/Properties",
                "Resources/AWS::Route53::RecordSetGroup/Properties/RecordSets/*",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_route53_recordset,
                filename="recordset_pattern.json",
            ),
            all_matches=True,
        )
