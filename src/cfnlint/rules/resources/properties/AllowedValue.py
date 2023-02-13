"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import ValidationError, _utils
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
                        yield from self.child_rules["W2030"].validate(v, enums)
                        return
        if instance in (0, 1):
            unbooled = _utils.unbool(instance)
            if all(unbooled != _utils.unbool(each) for each in enums):
                yield ValidationError(f"{instance!r} is not one of {enums!r}")
        elif instance not in enums:
            yield ValidationError(f"{instance!r} is not one of {enums!r}")
