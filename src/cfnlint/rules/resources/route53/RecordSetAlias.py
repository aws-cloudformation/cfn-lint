"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.extensions.aws_route53_recordset
from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class RecordSetAlias(CfnLintJsonSchema):
    """Check Route53 Recordset Configuration"""

    id = "E3029"
    shortdesc = "Validate Route53 record set aliases"
    description = (
        "When using alias records you can't specify TTL or certain types are allowed"
    )
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
                filename="recordset_alias.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "Additional properties are not allowed ('TTL' was unexpected)"
