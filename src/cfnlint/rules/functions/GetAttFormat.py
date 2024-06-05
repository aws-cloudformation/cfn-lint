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
        "Validate that if source and destination format exists that they match"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["parameters", "ec2", "imageid"]

    def __init__(self):
        super().__init__(["*"])
        self.parent_rules = ["E1010"]
        self._exceptions = [
            # Need to measure for completeness of automation
            "AWS::EC2::SecurityGroup.GroupId",
            "AWS::EC2::SecurityGroup.GroupIds",
        ]

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        fmt = schema.get("format")
        if not fmt or fmt in self._exceptions:
            return

        resource, attr = instance[0:2]

        getatt_fmt = validator.context.resources[resource].get_atts[attr]

        if getatt_fmt != fmt:
            yield ValidationError(
                (
                    f"{instance!r} creates {getatt_fmt!r} that does not "
                    f"match {fmt!r}"
                ),
                rule=self,
            )
