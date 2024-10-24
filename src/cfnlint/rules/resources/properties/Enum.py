"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema._keywords import enum, enumCaseInsensitive
from cfnlint.rules import CloudFormationLintRule


class Enum(CloudFormationLintRule):
    """Check if properties have a valid value"""

    id = "E3030"
    shortdesc = "Check if properties have a valid value"
    description = "Check if properties have a valid value in case of an enumator"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#enum"
    tags = ["resources", "property", "allowed value"]
    child_rules = {
        "W2030": None,
    }

    def enum(self, validator, enums, instance, schema):
        if (
            len(validator.context.path.value_path) > 0
            and validator.context.path.value_path[0] == "Parameters"
        ):
            if self.child_rules.get("W2030"):
                yield from self.child_rules["W2030"].enum(
                    validator, enums, instance, schema
                )
            return
        yield from enum(validator, enums, instance, schema)

    def enumCaseInsensitive(self, validator, enums, instance, schema):
        if (
            len(validator.context.path.value_path) > 0
            and validator.context.path.value_path[0] == "Parameters"
        ):
            if self.child_rules.get("W2030"):
                yield from self.child_rules["W2030"].enumCaseInsensitive(
                    validator, enums, instance, schema
                )
            return
        yield from enumCaseInsensitive(validator, enums, instance, schema)
