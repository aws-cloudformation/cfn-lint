"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from typing import Any, Callable, Dict, Iterator, Sequence

import cfnlint.jsonschema._validators as validators_standard
from cfnlint.context.value import ValueType
from cfnlint.helpers import (
    FUNCTIONS,
    FUNCTIONS_LIST,
    FUNCTIONS_OBJECT,
    FUNCTIONS_SINGLE,
    PSEUDOPARAMS,
    PSEUDOPARAMS_MULTIPLE,
    PSEUDOPARAMS_SINGLE,
    ToPy,
)
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.template.functions.exceptions import Unpredictable

_singular_types = ["string", "boolean", "number", "integer"]


def additionalProperties(
    validator: Validator, aP: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    for err in validators_standard.additionalProperties(
        validator, aP, instance, schema
    ):
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


def _fn_obj(functions: Sequence[str]) -> Iterator[ValidationError]:
    return {
        "minProperties": 1,
        "maxProperties": 1,
        "properties": dict.fromkeys(functions, True),
    }


class Fn:
    def __init__(self) -> None:
        self.types = []
        self.supported_functions = []

    def schema_function(self, functions: Sequence[str]) -> Iterator[ValidationError]:
        return {}

    def is_valid(
        self, validator: Validator, instance: Any, schema: Any, fn: ToPy | None = None
    ) -> Iterator[ValidationError]:
        try:
            fn_name = None
            if fn is not None:
                fn_name = fn.py
            err = next(validator.descend(instance, schema, fn_name, None))
            if fn is not None:
                err.validator = fn.py
            yield err
        except StopIteration:
            pass


class Scalar(Fn):
    def __init__(self) -> None:
        self.types = ["string"]
        self.supported_functions = []

    def schema_function(
        self, functions: Sequence[str] | None = None
    ) -> Iterator[ValidationError]:
        functions = functions or []
        return {"type": self.types}

    def is_valid(
        self, validator: Validator, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        try:
            err = next(validator.descend(instance, self.schema_function(), None, None))
            yield err
        except StopIteration:
            pass


class FnScalar(Fn):
    def __init__(self, name: str) -> None:
        self.types = []
        self.fn = ToPy(name)
        self.supported_functions = []

    def schema_function(self, functions: Sequence[str]) -> Iterator[ValidationError]:
        return {
            "minProperties": 1,
            "maxProperties": 1,
            "properties": dict.fromkeys(functions, True),
        }

    def is_valid(
        self, validator: Validator, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        if not validator.is_type(instance, "object"):
            return

        value = instance.get(self.fn.py)
        for err in super().is_valid(validator, value, {"type": self.types}, self.fn):
            yield err
            return

        if validator.is_type(value, "object"):
            for err in super().is_valid(
                validator,
                value,
                self.schema_function(self.supported_functions),
                self.fn,
            ):
                yield err
                return


class FnArray(Fn):
    def __init__(self, name: str, min_length: int, max_length: int) -> None:
        super().__init__()
        self.types = ["array"]
        self.fn = ToPy(name)
        self._min_length = min_length
        self._max_length = max_length
        self.items: Sequence[Fn] = []

    def schema_function(self) -> Iterator[ValidationError]:
        return {
            "minItems": self._min_length,
            "maxItems": self._max_length,
            "type": "array",
        }

    def item_function(self, functions: Sequence[str]) -> Iterator[ValidationError]:
        return {
            "minProperties": 1,
            "maxProperties": 1,
            "properties": dict.fromkeys(functions, True),
        }

    def is_valid(
        self, validator: Validator, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        if not validator.is_type(instance, "object"):
            return

        value = instance.get(self.fn.name)
        for err in super().is_valid(validator, value, self.schema_function()):
            yield err
            return

        if validator.is_type(value, "array"):
            for i, item in enumerate(self.items):
                yield from item.is_valid(validator, value[i], schema)


class Ref(FnScalar):
    def __init__(self) -> None:
        super().__init__("Ref")
        self.types.append("string")

    def ref(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        if validator.context.transforms.has_language_extensions_transform():
            self.types.append("object")
            self.supported_functions.append("Ref")

        for err in self.is_valid(validator, instance, schema):
            yield err
            return

        if validator.is_type(instance, "string"):
            valid_refs = (
                PSEUDOPARAMS
                + list(validator.context.parameters.keys())
                + list(validator.context.resources.keys())
            )
            yield from self.descend(validator, instance, {"enum": valid_refs})


# pylint: disable=unused-argument
def fn_getatt(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::GetAtt")


class FnBase64(FnScalar):
    def __init__(self) -> None:
        super().__init__("Fn::Base64")
        self.types.extend(["string", "object"])

    def base64(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        self.supported_functions = FUNCTIONS_SINGLE

        yield from self.validator(validator, s, instance, schema)


class FnGetAZs(FnScalar):
    def __init__(self) -> None:
        super().__init__("Fn::GetAZs")
        self.types.extend(["string", "object"])
        self.supported_functions.append("Ref")

    def get_azs(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        yield from self.validator(validator, s, instance, schema)

        if validator.is_type(instance, "string"):
            valid_refs = ["AWS::Region"] + list(validator.context.parameters.keys())
            yield from validator.descend(
                self.value(instance), {"enum": valid_refs}, None, None
            )


class FnImportalue(FnScalar):
    def __init__(self) -> None:
        super().__init__("Fn::ImportValue")
        self.types.extend(["string", "object"])
        self.supported_functions.extend(
            [
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Select",
                "Fn::Split",
                "Fn::Sub",
                "Ref",
            ]
        )

    def import_value(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        yield from self.validator(validator, s, instance, schema)


class FnJoin(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Join", 2, 2)
        self.items.append(Scalar())
        values = Scalar()
        values.types.append("array")
        self.items.append(values)

        self.supported_functions.extend(
            [
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Select",
                "Fn::Split",
                "Fn::Sub",
                "Ref",
            ]
        )

    def join(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance, schema):
            yield err
            return

        # we have to validate the second element manually
        values = instance.get(self.fn.name)[1]

        if validator.is_type(values, "object"):
            for err in validator.descend(
                values,
                schema={
                    "minProperties": 1,
                    "maxProperties": 1,
                    "properties": dict.fromkeys(FUNCTIONS_LIST, True),
                },
            ):
                yield err
                return

        if validator.is_type(values, "array"):
            for value in values:
                for err in validator.descend(
                    values,
                    schema={
                        "minProperties": 1,
                        "maxProperties": 1,
                        "properties": dict.fromkeys(FUNCTIONS_LIST, True),
                    },
                ):
                    yield err
                    return


# pylint: disable=unused-argument
def fn_join(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    fn_name = "Fn::Join"
    if not validator.is_type(instance, "object"):
        return

    join = instance.get(fn_name)

    join_schema = {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "items": [
            {"type": "string"},
            {"type": ["array", "object"]},
        ],
    }

    for err in validator.descend(join, join_schema, fn_name, None):
        err.validator = "fn_join"
        yield err
        return

    if validator.is_type(join[1], "array"):
        for i, value in enumerate(join[1]):
            for err in validator.descend(
                value, {"type": ["string", "object"]}, fn_name, None
            ):
                err.validator = "fn_join"
                err.path.append(1)
                err.path.append(i)
                yield err
                return

            if validator.is_type(value, "object"):
                for err in validator.descend(
                    value, _fn_obj(FUNCTIONS_SINGLE), fn_name, None
                ):
                    err.validator = "fn_join"
                    err.path.append(1)
                    err.path.append(i)
                    yield err
                return

        return

    for err in validator.descend(join[1], _fn_obj(FUNCTIONS_LIST), fn_name, None):
        err.validator = "fn_join"
        err.path.append(1)
        yield err


# pylint: disable=unused-argument
def fn_split(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    fn_name = "Fn::Split"
    if not validator.is_type(instance, "object"):
        return

    split = instance.get(fn_name)

    split_schema = {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "items": [
            {"type": "string"},
            {"type": ["string", "object"]},
        ],
    }

    for err in validator.descend(split, split_schema, fn_name, None):
        err.validator = "fn_split"
        yield err
        return

    for err in validator.descend(split[1], _fn_obj(FUNCTIONS_SINGLE), fn_name, None):
        err.validator = "fn_split"
        err.path.append(1)
        yield err


# pylint: disable=unused-argument
def fn_findinmap(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    yield from _fn(validator, s, instance, "Fn::FindInMap")


# pylint: disable=unused-argument
def fn_select(
    validator: Validator, s: Any, instance: Any, schema: Any
) -> Iterator[ValidationError]:
    fn_name = "Fn::Select"
    if not validator.is_type(instance, "object"):
        return

    select_schema = {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "items": [
            {"type": ["integer", "object"]},
            {"type": ["array", "object"]},
        ],
    }
    select = instance.get(fn_name)

    for err in validator.descend(select, select_schema, fn_name, None):
        err.validator = "fn_select"
        yield err
        return

    if validator.is_type(select[0], "object"):
        for err in validator.descend(
            select[0], _fn_obj(["Ref", "Fn::FindInMap"]), fn_name, None
        ):
            err.validator = "fn_select"
            err.path.append(0)
            yield err
        return

    if validator.is_type(select[1], "array"):
        for i, value in enumerate(select[1]):
            for err in validator.descend(
                value, {"type": ["string", "object"]}, fn_name, None
            ):
                err.validator = "fn_select"
                err.path.append(1)
                err.path.append(i)
                yield err
                return

            if validator.is_type(value, "object"):
                for err in validator.descend(value, _fn_obj(FUNCTIONS), fn_name, None):
                    err.validator = "fn_select"
                    err.path.append(1)
                    err.path.append(i)
                    yield err
                return

        return
    if validator.is_type(select, "object"):
        for err in validator.descend(select[1], _fn_obj(FUNCTIONS_LIST), None, None):
            err.validator = "fn_select"
            err.path.append(1)


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
    if not any(raw_type_fn(validator, type, instance) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


cfn_validators: Dict[str, V] = {
    "additionalProperties": additionalProperties,
    "type": cfn_type,
    "ref": Ref().ref,
    "fn_base64": FnBase64().base64,
    "fn_cidr": fn_cidr,
    "fn_if": fn_if,
    "fn_findinmap": fn_findinmap,
    "fn_getatt": fn_getatt,
    "fn_getazs": FnGetAZs().get_azs,
    "fn_importvalue": FnImportalue().import_value,
    "fn_join": FnJoin().join,
    "fn_length": fn_length,
    "fn_select": fn_select,
    "fn_split": fn_split,
    "fn_sub": fn_sub,
    "fn_tojsonstring": fn_tojsonstring,
}
