"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.helpers import VALID_PARAMETER_TYPES
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class Types(CfnLintKeyword):
    """Check if Parameters are typed"""

    id = "E2002"
    shortdesc = "Parameters have appropriate type"
    description = "Making sure the parameters have a correct type"
    source_url = (
        "https://docs.aws.amazon.com/AWSCloudFormation/latest/"
        "UserGuide/best-practices.html#parmtypes"
    )
    tags = ["parameters"]

    def __init__(self) -> None:
        super().__init__(keywords=["Parameters/*/Type"])

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        # Check if it's a valid documented type
        if instance in VALID_PARAMETER_TYPES:
            return

        # Undocumented AWS-qualified types may be accepted by CloudFormation,
        # but misspelled base types inside List or SSM wrappers are rejected.
        if instance.startswith(("AWS::SSM::Parameter::Value<", "List<")):
            base_type = instance
            while True:
                if (\n                    base_type.startswith("AWS::SSM::Parameter::Value<")\n                    and base_type.endswith(">")\n                ):
                    base_type = base_type[len("AWS::SSM::Parameter::Value<") : -1]
                elif base_type.startswith("List<") and base_type.endswith(">"):
                    base_type = base_type[len("List<") : -1]
                else:
                    break

            if "::" not in base_type and base_type not in (
                "String",
                "Number",
                "CommaDelimitedList",
            ):
                yield ValidationError(
                    f"{instance!r} has an invalid base parameter type {base_type!r}",
                    rule=self,
                )
            return

        # Invalid type
        yield ValidationError(
            f"{instance!r} is not one of {sorted(VALID_PARAMETER_TYPES)!r}",
            rule=self,
        )
