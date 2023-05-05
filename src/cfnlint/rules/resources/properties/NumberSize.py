"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import _validators
from cfnlint.rules.BaseJsonSchemaValidator import BaseJsonSchemaValidator


class NumberSize(BaseJsonSchemaValidator):
    """Check if a Number has a length within the limit"""

    id = "E3034"
    shortdesc = "Check if a number is between min and max"
    description = "Check numbers (integers and floats) for its value being between the minimum and maximum"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "number", "size"]

    # pylint: disable=unused-argument
    def validate_value(
        self, validator, enums, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        yield from kwargs["fn"](validator, enums, instance, schema)

    # pylint: disable=unused-argument
    def validate_if(
        self, validator, enums, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        if validator.is_type(instance, "array") and len(instance, 3):
            yield from kwargs["r_fn"](validator, enums, instance[1], schema)
            yield from kwargs["r_fn"](validator, enums, instance[2], schema)

    # pylint: disable=unused-argument
    def maximum(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
            fn=_validators.maximum,
            r_fn=self.maximum,
        )

    # pylint: disable=unused-argument
    def minimum(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
            fn=_validators.minimum,
            r_fn=self.minimum,
        )

    # pylint: disable=unused-argument
    def exclusiveMaximum(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
            fn=_validators.exclusiveMaximum,
            r_fn=self.exclusiveMaximum,
        )

    # pylint: disable=unused-argument
    def exclusiveMinimum(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
            fn=_validators.exclusiveMinimum,
            r_fn=self.exclusiveMinimum,
        )
