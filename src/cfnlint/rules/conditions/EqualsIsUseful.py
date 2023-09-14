"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class EqualsIsUseful(CloudFormationLintRule):
    """
    Validate that the Equals will return
    true/false and not always be true or false
    """

    id = "W8003"
    shortdesc = "Fn::Equals will always return true or false"
    description = (
        "Validate Fn::Equals to see if its comparing two strings or two equal items."
        " While this works it may not be intended."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-equals"
    tags = ["functions", "equals"]

    def equals_is_useful(self, validator, s, instance, schema):
        if not validator.is_type(instance, "array"):
            return

        if json.dumps(instance[0]) == json.dumps(instance[1]):
            yield ValidationError(f"{instance!r} will always return {True!r}")
        elif isinstance(instance[0], str) and isinstance(instance[1], str):
            yield ValidationError(f"{instance!r} will always return {False!r}")
