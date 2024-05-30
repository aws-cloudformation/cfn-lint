"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class GetAttFormat(CfnLintKeyword):
    id = "E1040"
    shortdesc = "Check if GetAtt matches destination format"
    description = (
        "Validate that if source and destination format exists " "that they match"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["parameters", "ec2", "imageid"]

    def __init__(self):
        super().__init__(["*"])
        self.parent_rules = ["E1010"]

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        resource, attr = instance[0:2]

        format = validator.context.resources[resource].get_atts[attr].format
        schema_format = schema.get("format")
        if schema_format:
            if format != schema_format:
                yield ValidationError(
                    (
                        f"{instance!r} creates {format!r} that does not "
                        f"match {schema_format!r}"
                    ),
                    rule=self,
                )
