"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema._keywords import enum
from cfnlint.rules import CloudFormationLintRule


class Enum(CloudFormationLintRule):
    """Check if parameters have a valid value"""

    id = "W2030"
    shortdesc = "Check if parameters have a valid value"
    description = (
        "Check if parameters have a valid value in case of an enumator. The Parameter's"
        " allowed values is based on the usages in property (Ref)"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#enum"
    tags = ["parameters", "resources", "property", "allowed value"]

    # This rule is triggered from the equivalent rule E3030
    # the values are fed from there and we adjust the error outputs
    # appropriately

    def enum(self, validator, enums, instance, schema):
        for err in enum(validator, enums, instance, schema):
            err.rule = self
            err.path_override = validator.context.path.value_path
            yield err
