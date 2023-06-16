"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from collections import deque
from typing import Any, Callable, Dict, Iterator

from cfnlint.context.value import ValueType
from cfnlint.helpers import (
    FUNCTIONS,
    FUNCTIONS_LIST,
    FUNCTIONS_SINGLE,
    PSEUDOPARAMS_MULTIPLE,
    PSEUDOPARAMS_SINGLE,
)
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.jsonschema._validators import (
    additionalProperties as additionalPropertiesStandard,
)
from cfnlint.template.functions.exceptions import Unpredictable

_singular_types = ["string", "boolean", "number", "integer"]


def additionalProperties(
    validator: Validator, aP: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    for err in additionalPropertiesStandard(validator, aP, instance, schema):
        if len(err.path) > 0:
            if err.path[0] not in FUNCTIONS:
                yield err
        else:
            yield err


def _fn(
    validator: Validator, schema: Any, instance: Any, fn: str
) -> Iterator[ValidationError]:
    if not validator.cfn:
        return
    try:
        for value in validator.cfn.functions.get_value(
            instance, validator.context.region
        ):
            evolved = validator.evolve(
                schema=schema,
                context=validator.context.evolve(
                    value=value,
                    path=deque([fn]),
                ),
            )
            for err in evolved.iter_errors(instance=value.value):
                err.message = err.message.replace(f"{err.instance!r}", f"{instance!r}")
                if value.value_type == ValueType.FUNCTION:
                    err.path_override = value.path
                err.path.extendleft(list(instance.keys()))
                yield err
    except Unpredictable:
        evolved = validator.evolve(
            function_filter=validator.function_filter.evolve(functions=[]),
            schema=schema,
            context=validator.context.evolve(
                path=deque([fn]),
            ),
        )
        for err in evolved.iter_errors(instance=instance):
            err.path.extendleft(list(instance.keys()))
            yield err


# pylint: disable=unused-argument
def ref(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    if instance == {"Ref": "AWS::NoValue"}:
        return
    yield from _fn(validator, s, instance, "Ref")


# pylint: disable=unused-argument
def fn_getatt(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::GetAtt")


# pylint: disable=unused-argument
def fn_base64(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Base64")


# pylint: disable=unused-argument
def fn_getazs(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::GetAZs")


# pylint: disable=unused-argument
def fn_importvalue(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::ImportValue")


# pylint: disable=unused-argument
def fn_join(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Join")


# pylint: disable=unused-argument
def fn_split(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Split")


# pylint: disable=unused-argument
def fn_findinmap(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::FindInMap")


# pylint: disable=unused-argument
def fn_select(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Select")


def fn_if(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    _instance = instance.get("Fn::If")
    if validator.is_type(_instance, "array") and len(_instance) == 3:
        for i in [1, 2]:
            for err in validator.descend(
                _instance[i],
                s,
            ):
                err.path.extendleft([i, "Fn::If"])
                yield err


# pylint: disable=unused-argument
def fn_sub(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Sub")


# pylint: disable=unused-argument
def fn_cidr(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Cidr")


# pylint: disable=unused-argument
def fn_length(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::Length")


# pylint: disable=unused-argument
def fn_tojsonstring(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::ToJsonString")


def _raw_type(validator: Validator, tS: Any, instance: Any) -> bool:
    if tS in ["object", "array"]:
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
        if instance in ["true", "false", "True", "False"]:
            return True
    return False


def _raw_type_strict(validator: Validator, tS: Any, instance: Any) -> bool:
    return validator.is_type(instance, tS)


def _cfn_type(
    validator: Validator,
    tS: Any,
    instance: Any,
    raw_type_fn: Callable[[Validator, Any, Any], bool],
) -> bool:
    if validator.is_type(instance, tS):
        if tS == "object":
            if len(instance) == 1:
                k = next(iter(instance), "")
                v = instance.get(k, [])
                # special exception as a GetAtt can return an object
                # Select an object from an array of objects
                if k in ["Fn::GetAtt", "Fn::Select"]:
                    return True
                if k == "Ref" or k in FUNCTIONS_LIST or k in FUNCTIONS_SINGLE:
                    return False
        return raw_type_fn(validator, tS, instance)

    if not validator.is_type(instance, "object"):
        return raw_type_fn(validator, tS, instance)

    if len(instance) == 1:
        k = next(iter(instance), "")
        v = instance.get(k, [])
        if k == "Ref":
            if v in PSEUDOPARAMS_SINGLE:
                if tS in _singular_types:
                    return True
                return False
            if v in PSEUDOPARAMS_MULTIPLE:
                if "array" in tS:
                    return True
                return False
        if tS == "array":
            if k in FUNCTIONS_LIST:
                return True
        if tS in _singular_types:
            if k in FUNCTIONS_SINGLE:
                # Length cannot return boolean
                if k == "Fn::Length":
                    return raw_type_fn(validator, tS, 0)
                # Base64, ToJsonString only return strings
                if k in ["Fn::ToJsonString", "Fn::Base64"] and "string" != tS:
                    return False
                return True
            return False
    return raw_type_fn(validator, tS, instance)


# pylint: disable=unused-argument
def cfn_type(
    validator: Validator, tS: Any, instance: Any, schema: Any, strict: bool = False
):
    """
    When evaluating a type in CloudFormation we have to account
    for the intrinsic functions that the values can represent
    (Ref, GetAtt, If, ...).  This will evaluate if the correct type
    is not found and the instance is an object with a function
    that we do our best to evaluate if that function represents the
    type we are looking for
    """
    if strict:
        raw_type_fn = _raw_type_strict
    else:
        raw_type_fn = _raw_type
    tS = ensure_list(tS)
    if not any(_cfn_type(validator, type, instance, raw_type_fn) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


cfn_validators: Dict[str, V] = {
    "additionalProperties": additionalProperties,
    "type": cfn_type,
    "ref": ref,
    "fn_base64": fn_base64,
    "fn_cidr": fn_cidr,
    "fn_if": fn_if,
    "fn_findinmap": fn_findinmap,
    "fn_getatt": fn_getatt,
    "fn_getazs": fn_getazs,
    "fn_importvalue": fn_importvalue,
    "fn_join": fn_join,
    "fn_length": fn_length,
    "fn_select": fn_select,
    "fn_split": fn_split,
    "fn_sub": fn_sub,
    "fn_tojsonstring": fn_tojsonstring,
}
