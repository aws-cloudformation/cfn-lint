"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

import regex as re

from cfnlint.helpers import REGEX_SUB_PARAMETERS
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules import CloudFormationLintRule


class SubParametersUsed(CloudFormationLintRule):
    """Check if Sub Parameters are used"""

    id = "W1019"
    shortdesc = "Validate that parameters to a Fn::Sub are used"
    description = "Validate that Fn::Sub Parameters are used"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if validator.is_type(instance, "string"):
            return

        variables = re.findall(REGEX_SUB_PARAMETERS, instance[0])
        for v, _ in instance[1].items():
            if v not in variables:
                yield ValidationError(
                    f"Parameter {v!r} not used in 'Fn::Sub'", path=deque([1, v])
                )
