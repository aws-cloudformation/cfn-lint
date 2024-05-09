"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceEngineVersion(CfnLintJsonSchema):
    id = "E3691"
    shortdesc = "Validate DB Instance Engine and Engine Version"
    description = "Validate the engine along with the engine version"
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html#cfn-rds-dbinstance-engine"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="engine_version.json",
            ),
            all_matches=True,
        )

    def validate(self, validator, keywords, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        if validator.is_type(instance.get("Engine"), "string"):
            instance["Engine"] = instance["Engine"].lower()

        yield from super().validate(validator, keywords, instance, schema)
