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
from cfnlint.rules import CloudFormationLintRule


class StringSize(CloudFormationLintRule):
    """Check if a String has a length within the limit"""

    id = "E3033"
    shortdesc = "Check if a string has between min and max number of values specified"
    description = "Check strings for its length between the minimum and maximum"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "string", "size"]

    # pylint: disable=unused-argument
    def validate_fn_sub(
        self, validator, sS, instance, schema, fn
    ):  # pylint: disable=arguments-renamed
        if isinstance(instance, str):
            yield from fn(validator, sS, self._fix_sub_string(instance), schema)
        elif isinstance(instance, list) and len(instance) == 2:
            yield from fn(validator, sS, self._fix_sub_string(instance[0]), schema)

    def _serialize_date(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return json.JSONEncoder.default(self, o=obj)

    def _fix_sub_string(self, instance):
        return re.sub(r"\${[a-zA-Z0-9._-]{1,255}}", "", instance)

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
                                return self._fix_sub_string(v)
                            if isinstance(v, list):
                                return self._fix_sub_string(v[0])
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

    # pylint: disable=unused-argument, arguments-renamed
    def maxLength(self, validator, mL, instance, schema):
        if (
            validator.is_type(instance, "object")
            and validator.schema.get("type") == "object"
        ):
            yield from self._non_string_max_length(instance, mL)
        elif validator.is_type(instance, "string") and len(instance) > mL:
            yield ValidationError(f"{instance!r} is longer than {mL}")

    # pylint: disable=unused-argument, arguments-renamed
    def minLength(self, validator, mL, instance, schema):
        if (
            validator.is_type(instance, "object")
            and validator.schema.get("type") == "object"
        ):
            yield from self._non_string_min_length(instance, mL)
        elif validator.is_type(instance, "string") and len(instance) < mL:
            yield ValidationError(f"{instance!r} is shorter than {mL}")
