"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema._keywords import (
    exclusiveMaximum,
    exclusiveMinimum,
    maximum,
    minimum,
)
from cfnlint.rules import CloudFormationLintRule


class NumberRange(CloudFormationLintRule):
    """Check if a Number has a length within the limit"""

    id = "E3034"
    shortdesc = "Check if a number is between min and max"
    description = (
        "Check numbers (integers and floats) for its value being between the minimum"
        " and maximum"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#number-range"
    tags = ["resources", "property", "number", "size"]
    child_rules = {
        "W3034": None,
    }

    def __init__(self) -> None:
        self.parameter_rule = "W3034"
        super().__init__()

    def minimum(self, validator, m, instance, schema):
        if (
            len(validator.context.path.value_path) > 0
            and validator.context.path.value_path[0] == "Parameters"
        ):
            if self.child_rules.get(self.parameter_rule):
                yield from self.child_rules[self.parameter_rule].validate(
                    validator, m, instance, schema, minimum
                )
            return
        yield from minimum(validator, m, instance, schema)

    def maximum(self, validator, m, instance, schema):
        if (
            len(validator.context.path.value_path) > 0
            and validator.context.path.value_path[0] == "Parameters"
        ):
            if self.child_rules.get(self.parameter_rule):
                yield from self.child_rules[self.parameter_rule].validate(
                    validator, m, instance, schema, maximum
                )
            return
        yield from maximum(validator, m, instance, schema)

    def exclusiveMaximum(self, validator, m, instance, schema):
        if (
            len(validator.context.path.value_path) > 0
            and validator.context.path.value_path[0] == "Parameters"
        ):
            if self.child_rules.get(self.parameter_rule):
                yield from self.child_rules[self.parameter_rule].validate(
                    validator, m, instance, schema, exclusiveMaximum
                )
            return
        yield from exclusiveMaximum(validator, m, instance, schema)

    def exclusiveMinimum(self, validator, m, instance, schema):
        if (
            len(validator.context.path.value_path) > 0
            and validator.context.path.value_path[0] == "Parameters"
        ):
            if self.child_rules.get(self.parameter_rule):
                yield from self.child_rules[self.parameter_rule].validate(
                    validator, m, instance, schema, exclusiveMinimum
                )
            return
        yield from exclusiveMinimum(validator, m, instance, schema)
