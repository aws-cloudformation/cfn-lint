"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import TEMPLATED_PROPERTY_CFN_PATHS, ensure_list
from cfnlint.jsonschema._keywords_cfn import cfn_type
from cfnlint.rules import CloudFormationLintRule


class Type(CloudFormationLintRule):
    """Check if Resource PrimitiveTypes are correct"""

    id = "E3012"
    shortdesc = "Check resource properties values"
    description = (
        "Checks resource property values with Primitive Types for values that match"
        " those types."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#type"
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

    # pylint: disable=unused-argument
    def type(self, validator, types, instance, schema):
        if validator.context.path.cfn_path:
            if (
                validator.is_type(instance, "string")
                and not validator.context.strict_types
            ):
                if (
                    "/".join(validator.context.path.cfn_path)
                    in TEMPLATED_PROPERTY_CFN_PATHS
                ):
                    return

        if (
            self.config.get("strict") or validator.context.strict_types
        ) and not validator.context.is_resolved_value:
            validator = validator.evolve(
                context=validator.context.evolve(strict_types=True)
            )
        else:
            validator = validator.evolve(
                context=validator.context.evolve(strict_types=False)
            )

        types = ensure_list(types)
        for err in cfn_type(
            validator,
            types,
            instance,
            schema,
        ):
            for t in ["object", "array", "boolean", "integer", "number", "string"]:
                if validator.is_type(instance, t):
                    err.extra_args = {
                        "actual_type": t,
                        "expected_type": types[0],
                    }
                    yield err
                    break
