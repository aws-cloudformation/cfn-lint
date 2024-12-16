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

        if len(instance) != 2:
            return

        # testing on 2023/09/24
        # True (boolean) != "True"
        # True (boolean) == "true"
        # 1 == "1"
        if json.dumps(instance[0]) == json.dumps(instance[1]):
            yield ValidationError(
                f"{instance!r} will always return {True!r} or {False!r}",
                rule=self,
            )
            return
        try:
            first = instance[0]
            second = instance[1]
            if validator.is_type(first, "boolean"):
                first = "true" if first else "false"
            if validator.is_type(second, "boolean"):
                first = "true" if first else "false"
            if str(first) == str(second):
                yield ValidationError(
                    f"{instance!r} will always return {True!r}",
                    rule=self,
                )
            if isinstance(instance[0], (str, float, int, bool)) and isinstance(
                instance[1], (str, float, int, bool)
            ):
                if str(first) != str(second):
                    yield ValidationError(
                        f"{instance!r} will always return {False!r}",
                        rule=self,
                    )
        except:  # noqa: E722
            pass
