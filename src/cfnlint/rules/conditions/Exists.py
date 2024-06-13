"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules import CloudFormationLintRule


class Exists(CloudFormationLintRule):
    """Check if used Conditions are defined"""

    id = "E8002"
    shortdesc = "Check if the referenced Conditions are defined"
    description = (
        "Making sure the used conditions are actually defined in the Conditions section"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html"
    tags = ["conditions"]

    def cfncondition(self, validator: Validator, conditions, instance: Any, schema):
        if not validator.is_type(instance, "string"):
            return
        for err in validator.descend(
            instance, {"enum": list(validator.context.conditions.conditions.keys())}
        ):
            err.rule = self
            yield err
