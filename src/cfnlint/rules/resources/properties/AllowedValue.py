"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import _validators
from cfnlint.rules import CloudFormationLintRule


class AllowedValue(CloudFormationLintRule):
    """Check if properties have a valid value"""

    id = "E3030"
    shortdesc = "Check if properties have a valid value"
    description = "Check if properties have a valid value in case of an enumator"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue"
    tags = ["resources", "property", "allowed value"]
    child_rules = {
        "W2030": None,
    }

    # pylint: disable=unused-argument
    def enum(self, validator, enums, instance, schema):
        if isinstance(instance, dict):
            if len(instance) == 1:
                for k, v in instance.items():
                    if k == "Ref":
                        if self.child_rules.get("W2030"):
                            yield from self.child_rules["W2030"].validate(v, enums)
                        return
        yield from _validators.enum(validator, enums, instance, schema)
