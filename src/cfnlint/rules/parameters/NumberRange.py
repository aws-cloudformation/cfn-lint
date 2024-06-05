"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class NumberRange(CloudFormationLintRule):
    """Check if a Number has a length within the limit"""

    id = "W3034"
    shortdesc = "Check if parameter values are between min and max"
    description = (
        "Check if parameter values value being between the minimum" " and maximum"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#number-size"
    tags = ["resources", "property", "number", "size"]

    def validate(self, validator, m, instance, schema, fn):
        for err in fn(validator, m, instance, schema):
            err.rule = self
            err.path_override = validator.context.path.value_path
            yield err
