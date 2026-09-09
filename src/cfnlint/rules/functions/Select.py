"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class Select(BaseFn):
    """Check if Select values are correct"""

    id = "E1017"
    shortdesc = "Select validation of parameters"
    description = "Making sure the Select function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html"
    tags = ["functions", "select"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Select",
            all_types,
            resolved_rule="W1035",
        )
        self.fn_select = self.validate

    def _index_out_of_bounds(
        self, validator: Validator, instance: Any
    ) -> ValidationResult:
        """Flag a literal index that is out of bounds for a literal list.

        CloudFormation fails ``CreateStack``/``UpdateStack`` at deploy time
        with "Fn::Select cannot select nonexistent value at index N" when the
        index is a hardcoded integer that is greater than or equal to the
        length of a hardcoded list. The length of a literal list is fixed at
        template authoring time (functions used as list *items* still each
        count as a single element), so this is always a definite error.
        """
        _, value = self.key_value(instance)
        if not validator.is_type(value, "array") or len(value) != 2:
            return

        index, obj = value[0], value[1]

        # Only a hardcoded, non-negative integer index is a definite failure.
        # A negative index is handled by the schema (minimum: 0) and a
        # function/Ref index can resolve to anything at deploy time.
        if validator.is_type(index, "string"):
            try:
                index = int(index)
            except ValueError:
                return
        if not validator.is_type(index, "integer") or index < 0:
            return

        # The list must be hardcoded for its length to be known statically.
        if not validator.is_type(obj, "array"):
            return

        if index >= len(obj):
            yield ValidationError(
                f"{index!r} is not a valid index for a list of length {len(obj)!r}",
                validator=self.fn.py,
                path=deque([self.fn.name, 0]),
            )

    def validate(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        errs = list(self._index_out_of_bounds(validator, instance))
        if errs:
            yield from iter(errs)
            return

        yield from super().validate(validator, s, instance, schema)
