"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class DynamicReferenceSpaces(CloudFormationLintRule):
    id = "W1053"
    shortdesc = "Dynamic references should not contain spaces"
    description = (
        "Dynamic references with spaces between '{{' and 'resolve' "
        "will not be resolved by CloudFormation and will be treated as "
        "a literal string"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html"
    tags = ["functions", "dynamic reference"]

    def dynamicReferenceSpaces(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ):
        yield ValidationError(
            f"{instance!r} has spaces and will not be resolved as a "
            f"dynamic reference. Remove spaces from '{{{{resolve:...}}}}'",
            rule=self,
        )
