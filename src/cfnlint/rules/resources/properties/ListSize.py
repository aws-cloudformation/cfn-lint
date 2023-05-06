"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema import _validators
from cfnlint.rules.BaseJsonSchemaValidator import BaseJsonSchemaValidator


class ListSize(BaseJsonSchemaValidator):
    """Check if List has a size within the limit"""

    id = "E3032"
    shortdesc = "Check if a list has between min and max number of values specified"
    description = "Check lists for the number of items in the list to validate they are between the minimum and maximum"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "list", "size"]

    # pylint: disable=unused-argument
    def validate_value(
        self, validator, mI, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        yield from kwargs["fn"](validator, mI, instance, schema)

    # pylint: disable=unused-argument
    def validate_if(
        self, validator, mI, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        if validator.is_type(instance, "array") and len(instance) == 3:
            yield from kwargs["r_fn"](validator, mI, instance[1], schema)
            yield from kwargs["r_fn"](validator, mI, instance[2], schema)

    # pylint: disable=unused-argument
    def maxItems(self, validator, mI, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=mI,
            instance=instance,
            schema=schema,
            fn=_validators.maxItems,
            r_fn=self.maxItems,
        )

    # pylint: disable=unused-argument
    def minItems(self, validator, mI, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=mI,
            instance=instance,
            schema=schema,
            fn=_validators.minItems,
            r_fn=self.minItems,
        )
