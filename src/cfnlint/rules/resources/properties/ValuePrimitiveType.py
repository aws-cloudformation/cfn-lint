"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema._utils import ensure_list
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules import CloudFormationLintRule


class ValuePrimitiveType(CloudFormationLintRule):
    """Check if Resource PrimitiveTypes are correct"""

    id = "E3012"
    shortdesc = "Check resource properties values"
    description = (
        "Checks resource property values with Primitive Types for values that match"
        " those types."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#valueprimitivetype"
    tags = ["resources"]

    strict_exceptions = {
        "AWS::CloudFormation::Stack": ["Parameters"],
        "AWS::Lambda::Function.Environment": ["Variables"],
    }

    def __init__(self):
        """Init"""
        super().__init__()
        self.config_definition = {
            "strict": {"default": False, "type": "boolean"},
        }  # Strict mode is set to false by default
        self.configure()
        self.cfn = None

    def initialize(self, cfn):
        self.cfn = cfn
        return super().initialize(cfn)

    # pylint: disable=unused-argument
    def type(self, validator, types, instance, schema):
        types = ensure_list(types)
        for err in cfn_type(
            validator, types, instance, schema, self.config.get("strict")
        ):
            for t in ["object", "array", "boolean", "integer", "number", "string"]:
                if validator.is_type(instance, t):
                    err.extra_args = {
                        "actual_type": t,
                        "expected_type": types[0],
                    }
                    yield err
                    break
