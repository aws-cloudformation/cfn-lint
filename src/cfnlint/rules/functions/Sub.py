"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._validators_cfn import FnSub
from cfnlint.rules import CloudFormationLintRule


class Sub(CloudFormationLintRule):
    """Check if Sub values are correct"""

    id = "E1019"
    shortdesc = "Sub validation of parameters"
    description = "Making sure the sub function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]

    def __init__(self) -> None:
        super().__init__()
        self.validate = FnSub().validate
        self.child_rules = {
            "W1019": None,
            "W1020": None,
        }

    def fn_sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        found = False
        for err in self.validate(validator, s, instance, schema):
            yield err
            found = True

        # we know the structure is valid at this point
        # so any child rule doesn't have to revalidate it
        if not found:
            for _, rule in self.child_rules.items():
                if rule:
                    for err in rule.validate(
                        validator, s, instance.get("Fn::Sub"), schema
                    ):
                        err.path.append("Fn::Sub")
                        err.rule = rule
                        yield err
