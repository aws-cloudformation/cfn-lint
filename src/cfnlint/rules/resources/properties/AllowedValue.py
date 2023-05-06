"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import _validators
from cfnlint.rules.BaseJsonSchemaValidator import BaseJsonSchemaValidator


class AllowedValue(BaseJsonSchemaValidator):
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
    def validate_value(
        self, validator, enums, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        yield from _validators.enum(validator, enums, instance, schema)

    # pylint: disable=unused-argument
    def validate_ref(
        self, validator, enums, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        if self.child_rules.get("W2030"):
            yield from self.child_rules["W2030"].validate(instance, enums)

    # pylint: disable=unused-argument
    def validate_if(
        self, validator, enums, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        if validator.is_type(instance, "array") and len(instance) == 3:
            yield from self.enum(validator, enums, instance[1], schema)
            yield from self.enum(validator, enums, instance[2], schema)

    # pylint: disable=unused-argument
    def enum(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
        )
