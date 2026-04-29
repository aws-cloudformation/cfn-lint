"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules import CloudFormationLintRule


class RawPseudoParameter(CloudFormationLintRule):
    """Check for pseudo-parameters used as plain strings without Ref"""

    id = "W1054"
    shortdesc = "Pseudo-parameter string found without Ref"
    description = (
        "A pseudo-parameter such as 'AWS::NoValue' or 'AWS::Region' "
        "was used as a plain string value. In most cases you want "
        "'Ref: AWS::...' instead of the raw string."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/pseudo-parameter-reference.html"
    tags = ["functions", "pseudo-parameter"]

    def rawPseudoParameter(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield ValidationError(
            f"{instance!r} is a pseudo-parameter and should "
            f"probably be used as 'Ref: {instance}' instead of a plain string",
            rule=self,
        )
