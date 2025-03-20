"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import regex as re

from cfnlint.helpers import REGEX_SUB_PARAMETERS, TRANSFORM_SAM, ensure_list
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules import CloudFormationLintRule


class SubUnneeded(CloudFormationLintRule):
    """Check if Sub is using a variable"""

    id = "W1020"
    shortdesc = "Sub isn't needed if it doesn't have a variable defined"
    description = "Checks sub strings to see if a variable is defined."
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if TRANSFORM_SAM in ensure_list(validator.cfn.transform_pre.get("Transform")):
            return
        if validator.is_type(instance, "string"):
            variables = re.findall(REGEX_SUB_PARAMETERS, instance)
            path = []
        else:
            variables = re.findall(REGEX_SUB_PARAMETERS, instance[0])
            path = [0]
        if not variables:
            yield ValidationError(
                "'Fn::Sub' isn't needed because there are no variables", path=path
            )
