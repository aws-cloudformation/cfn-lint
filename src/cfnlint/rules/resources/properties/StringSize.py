"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import datetime
import json
from typing import Any

import regex as re

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.BaseJsonSchemaValidator import BaseJsonSchemaValidator


class StringSize(BaseJsonSchemaValidator):
    """Check if a String has a length within the limit"""

    id = "E3033"
    shortdesc = "Check if a string has between min and max number of values specified"
    description = "Check strings for its length between the minimum and maximum"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "string", "size"]

    # pylint: disable=unused-argument
    def validate_value(
        self, validator, sS, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        yield from kwargs["fn"](validator, sS, instance, schema)

    # pylint: disable=unused-argument
    def validate_if(
        self, validator, sS, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        if validator.is_type(instance, "array") and len(instance) == 3:
            yield from kwargs["r_fn"](validator, sS, instance[1], schema)
            yield from kwargs["r_fn"](validator, sS, instance[2], schema)

    # pylint: disable=unused-argument
    def validate_sub(
        self, validator, sS, instance, schema, **kwargs
    ):  # pylint: disable=arguments-renamed
        yield from kwargs["fn"](validator, sS, kwargs["original_instance"], schema)

    def _serialize_date(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, o=obj)

    # pylint: disable=too-many-return-statements
    def _remove_functions(self, obj: Any) -> Any:
        """Replaces intrinsic functions with string"""
        if isinstance(obj, dict):
            new_obj = {}
            if len(obj) == 1:
                for k, v in obj.items():
                    if k in FUNCTIONS:
                        if k == "Fn::Sub":
                            if isinstance(v, str):
                                return re.sub(r"\${.*}", "", v)
                            if isinstance(v, list):
                                return re.sub(r"\${.*}", "", v[0])
                        else:
                            return ""
                    else:
                        new_obj[k] = self._remove_functions(v)
                        return new_obj
            else:
                for k, v in obj.items():
                    new_obj[k] = self._remove_functions(v)
                return new_obj
        elif isinstance(obj, list):
            new_list = []
            for v in obj:
                new_list.append(self._remove_functions(v))
            return new_list

        return obj

    def _non_string_max_length(self, instance, mL):
        j = self._remove_functions(instance)
        if len(json.dumps(j, separators=(",", ":"), default=self._serialize_date)) > mL:
            yield ValidationError("Item is too long")

    def _non_string_min_length(self, instance, mL):
        j = self._remove_functions(instance)
        if len(json.dumps(j, separators=(",", ":"), default=self._serialize_date)) < mL:
            yield ValidationError("Item is too short")

    # pylint: disable=unused-argument
    def _maxLength(self, validator, mL, instance, schema):
        if (
            validator.is_type(instance, "object")
            and validator.schema.get("type") == "object"
        ):
            yield from self._non_string_max_length(instance, mL)
        elif validator.is_type(instance, "string") and len(instance) > mL:
            yield ValidationError(f"{instance!r} is too long")

    # pylint: disable=unused-argument
    def _minLength(self, validator, mL, instance, schema):
        if (
            validator.is_type(instance, "object")
            and validator.schema.get("type") == "object"
        ):
            yield from self._non_string_min_length(instance, mL)
        elif validator.is_type(instance, "string") and len(instance) < mL:
            yield ValidationError(f"{instance!r} is too short")

    # pylint: disable=unused-argument
    def maxLength(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
            fn=self._maxLength,
            r_fn=self.maxLength,
        )

    # pylint: disable=unused-argument
    def minLength(self, validator, enums, instance, schema):
        yield from self.validate_instance(
            validator=validator,
            s=enums,
            instance=instance,
            schema=schema,
            fn=self._minLength,
            r_fn=self.minLength,
        )
