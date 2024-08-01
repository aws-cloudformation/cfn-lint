"""
Copyright (c) 2013 Julian Berman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

SPDX-License-Identifier: MIT
"""

# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from __future__ import annotations

from typing import Any

import regex as re

import cfnlint.jsonschema._keywords as validators_standard
from cfnlint.helpers import BOOLEAN_STRINGS, ensure_list
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V, ValidationResult


def additionalProperties(
    validator: Validator, aP: Any, instance: Any, schema: Any
) -> ValidationResult:
    for err in validators_standard.additionalProperties(
        validator, aP, instance, schema
    ):
        if len(err.path) > 0:
            if any(
                re.fullmatch(fn, str(err.path[0])) for fn in validator.context.functions
            ):
                continue
            yield err
        else:
            yield err


class FnItems:
    def validate(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        if not validator.is_type(instance, "array"):
            return

        if validator.is_type(s, "array"):
            for (index, item), subschema in zip(enumerate(instance), s):
                yield from validator.evolve(
                    context=validator.context.evolve(
                        functions=subschema.get("functions", []),
                        strict_types=False,
                    ),
                ).descend(
                    instance=item,
                    schema=subschema.get("schema", {}),
                    path=index,
                )
        else:
            for index, item in enumerate(instance):
                yield from validator.evolve(
                    context=validator.context.evolve(
                        functions=s.get("functions", []),
                        strict_types=False,
                    ),
                ).descend(
                    instance=item,
                    schema=s.get("schema", {}),
                    path=index,
                )


#####
# Type checks
#####
def _raw_type(validator: Validator, tS: Any, instance: Any) -> bool:
    if tS in ["object", "array", "null"] or validator.is_type(instance, "null"):
        return validator.is_type(instance, tS)
    if "string" == tS:
        if validator.is_type(instance, "object") or validator.is_type(
            instance, "array"
        ):
            return False
        return True
    if "number" == tS:
        if validator.is_type(instance, "boolean"):
            return False
        try:
            float(instance)
            return True
        except (ValueError, TypeError):
            return False
    if "integer" == tS:
        if validator.is_type(instance, "boolean"):
            return False
        try:
            int(instance)
            return True
        except (ValueError, TypeError):
            return False
    if "boolean" == tS:
        if validator.is_type(instance, "boolean"):
            return True
        if instance in list(BOOLEAN_STRINGS):
            return True
    return False


def _raw_type_strict(validator: Validator, tS: Any, instance: Any) -> bool:
    return validator.is_type(instance, tS)


# pylint: disable=unused-argument
def cfn_type(validator: Validator, tS: Any, instance: Any, schema: Any):
    """
    When evaluating a type in CloudFormation we have to account
    for the intrinsic functions that the values can represent
    (Ref, GetAtt, If, ...).  This will evaluate if the correct type
    is not found and the instance is an object with a function
    that we do our best to evaluate if that function represents the
    type we are looking for
    """
    if validator.context.strict_types:
        raw_type_fn = _raw_type_strict
    else:
        raw_type_fn = _raw_type
    tS = ensure_list(tS)
    if not any(raw_type_fn(validator, type, instance) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


cfn_validators: dict[str, V] = {
    "additionalProperties": additionalProperties,
    "fn_items": FnItems().validate,
    "type": cfn_type,
}
