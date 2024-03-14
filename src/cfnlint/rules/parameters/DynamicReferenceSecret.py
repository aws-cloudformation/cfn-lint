"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class DynamicReferenceSecret(CloudFormationLintRule):
    """
    Check if Dynamic Reference Secure Strings are
    only used in the correct locations
    """

    id = "W1011"
    shortdesc = "Instead of REFing a parameter for a secret use a dynamic reference"
    description = (
        "Instead of REFing a parameter for a secret use a dynamic reference. "
        "Solutions like SSM parameter store and secrets manager provide "
        "better security of sercrets"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/security-best-practices.html#creds"
    tags = ["functions", "dynamic reference", "ref"]

    def validate(self, validator: Validator, _, instance: Any, schema: Any):
        value = instance.get("Ref")

        if not validator.is_type(value, "string"):
            return

        if value in validator.context.parameters:
            yield ValidationError(
                "Use dynamic references over parameters for secrets", rule=self
            )
