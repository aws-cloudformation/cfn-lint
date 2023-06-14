"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema._validators import enum
from cfnlint.rules import CloudFormationLintRule


class AllowedValue(CloudFormationLintRule):
    """Check if parameters have a valid value"""

    id = "W2030"
    shortdesc = "Check if parameters have a valid value"
    description = (
        "Check if parameters have a valid value in case of an enumator. The Parameter's"
        " allowed values is based on the usages in property (Ref)"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue"
    tags = ["parameters", "resources", "property", "allowed value"]

    def __init__(self):
        super().__init__()

    def enum(self, validator, enums, instance, schema):
        for err in enum(validator, enums, instance, schema):
            err.rule = self
            err.path_override = validator.context.value.path
            yield err
