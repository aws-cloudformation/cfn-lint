"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import ValidationError
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

    def _unbool(self, element, true=object(), false=object()):
        if element is True:
            return true
        if element is False:
            return false
        return element

    # pylint: disable=unused-argument
    def enum(self, validator, enums, instance, schema):
        if isinstance(instance, dict):
            if len(instance) == 1:
                for k, v in instance.items():
                    if k == "Ref":
                        yield from self.child_rules["W2030"].validate(v, enums)
                        return
        if instance in (0, 1):
            unbooled = self._unbool(instance)
            if all(unbooled != self._unbool(each) for each in enums):
                yield ValidationError(f"{instance!r} is not one of {enums!r}")
        elif instance not in enums:
            yield ValidationError(f"{instance!r} is not one of {enums!r}")
