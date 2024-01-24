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

    def fn_sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from self.validate(validator, s, instance, schema)
