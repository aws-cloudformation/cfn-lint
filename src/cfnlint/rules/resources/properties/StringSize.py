"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import datetime
import json

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

    def _serialize_date(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )

    # pylint: disable=too-many-return-statements
    def _remove_functions(self, obj):
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

    # pylint: disable=unused-argument
    def maxLength(self, validator, mL, instance, schema):
        if validator.is_type(instance, "object"):
            yield from self._non_string_max_length(instance, mL)
        elif validator.is_type(instance, "string") and len(instance) > mL:
            yield ValidationError(f"{instance!r} is too long")
