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
from cfnlint.helpers import (
    BOOLEAN_STRINGS,
    FUNCTION_FOR_EACH,
    FUNCTION_TRANSFORM,
    ensure_list,
    is_function,
)
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V, ValidationResult

_ap_exception_fns = set([FUNCTION_TRANSFORM, FUNCTION_FOR_EACH])


def additionalProperties(
    validator: Validator, aP: Any, instance: Any, schema: Any
) -> ValidationResult:
    # is function will just return if one item is present
    # as this is the standard. We will handle exceptions below
    k, _ = is_function(instance)
    if k in validator.context.functions:
        return
    for err in validators_standard.additionalProperties(
        validator, aP, instance, schema
    ):
        # Some functions can exist at the same level
        # so we need to validate that if those functions are
        # currently supported by the context and are part of the
        # error

        # if the path is 0 just yield the error and return
        # this should never happen
        if not len(err.path) > 0:  # pragma: no cover
            yield err  # pragma: no cover
            return  # pragma: no cover

        for fn in list(_ap_exception_fns & set(validator.context.functions)):
            if re.fullmatch(fn, str(err.path[0])):  # type: ignore
                break
        else:
            yield err


def cfnContext(
    validator: Validator,
    s: Any,
    instance: Any,
    schema: Any,
) -> ValidationResult:

    context_parameters: dict[str, Any] = {}

    functions = s.get("functions")
    if functions is not None:
        if validator.is_type(functions, "object"):
            if "$ref" in functions:
                _, functions = validator.resolver.resolve(functions["$ref"])
            else:
                functions = []

    pseudo_parameters = s.get("pseudoParameters")
    if pseudo_parameters is not None:
        context_parameters["pseudo_parameters"] = set(pseudo_parameters)

    references = s.get("references")
    if references is not None:
        if "Resources" not in references:
            context_parameters["resources"] = {}

    if functions is not None:
        context_parameters["functions"] = functions

    cfn_validator = validator.evolve(
        context=validator.context.evolve(**context_parameters)
    )

    yield from cfn_validator.descend(
        instance=instance,
        schema=s.get("schema", {}),
        schema_path="schema",
    )


def dynamicValidation(
    validator: Validator, dV: Any, instance: Any, schema: dict[str, Any]
) -> ValidationResult:
    """
    Performs dynamic validation based on context.

    The dynamicValidation keyword supports:
    - context: The context source to validate against
               (parameters, conditions, resources, etc.)
    - transformCheck: Check if a specific transform exists
                      (returns true/false for if/then/else)
    - pathCheck: Validate based on the current path in the template
    """
    if not validator.is_type(dV, "object"):
        return

    # Handle transform check (for use with if/then/else)
    transform_check = dV.get("transformCheck")
    if transform_check is not None:
        if transform_check not in validator.context.transforms.transforms:
            yield ValidationError(
                (
                    f"Transform {transform_check!r} is required "
                    "but not present in the template"
                )
            )

    # Handle dynamic source validation
    context_source = dV.get("context")
    if context_source is not None:
        if context_source and isinstance(context_source, str):
            # Get the appropriate collection based on the context source
            collection = None
            if context_source == "conditions":
                collection = list(validator.context.conditions.conditions.keys())
            elif context_source == "mappings":
                collection = list(validator.context.mappings.maps.keys())
            elif context_source == "refs":
                collection = validator.context.refs

            if collection is not None:
                # Build a dynamic schema with an enum of valid values
                dynamic_schema = {"enum": collection}

                # Use descend to validate against the dynamic schema
                yield from validator.descend(
                    instance=instance,
                    schema=dynamic_schema,
                )

    path_check = dV.get("pathCheck")
    if path_check:
        current_path = "/".join(str(p) for p in validator.context.path.path)
        pattern_schema = {"pattern": f"^{path_check}.*$"}

        yield from validator.descend(
            instance=current_path,
            schema=pattern_schema,
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
    "cfnContext": cfnContext,
    "dynamicValidation": dynamicValidation,
    "type": cfn_type,
}
