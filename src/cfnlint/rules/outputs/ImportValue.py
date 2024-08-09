"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any, Iterator

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class ImportValue(CloudFormationLintRule):
    """Check if a Output is done of another output"""

    id = "W6001"
    shortdesc = "Check Outputs using ImportValue"
    description = (
        "Check if the Output value is set using ImportValue, so creating an Output of"
        " an Output"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["outputs", "importvalue"]

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        if len(validator.context.path.path) >= 3:
            if (
                validator.context.path.path[0] == "Outputs"
                and validator.context.path.path[2] == "Value"
            ):
                key = list(instance.keys())[0]
                yield ValidationError(
                    (f"The output value {instance!r} is an import from another output"),
                    rule=self,
                    path=deque([key]),
                )
