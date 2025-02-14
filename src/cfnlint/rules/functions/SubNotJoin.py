"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules import CloudFormationLintRule


class SubNotJoin(CloudFormationLintRule):
    id = "I1022"
    shortdesc = "Use Sub instead of Join"
    description = (
        "Prefer a sub instead of Join when using a join delimiter that is empty"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub", "join"]

    def _check_element(self, element):
        if isinstance(element, dict):
            if len(element) == 1:
                for key, value in element.items():
                    if key in ["Fn::Sub"]:
                        if not isinstance(value, str):
                            return False
                    elif key not in ["Ref", "Fn::GetAtt"]:
                        return False

        return True

    def _check_elements(self, elements):
        if not isinstance(elements, list):
            return False

        for element in elements:
            if not self._check_element(element):
                return False

        return True

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if validator.cfn.is_cdk_template():
            return

        key = list(instance.keys())[0]
        value = instance.get(key)

        if value[0] != "":
            return

        if self._check_elements(value[1]):
            yield ValidationError(
                ("Prefer using Fn::Sub over Fn::Join with an empty delimiter"),
                path=deque([key, 0]),
                rule=self,
            )
