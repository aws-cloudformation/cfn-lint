"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, Iterator, Sequence

import regex as re

import cfnlint.jsonschema._validators as validators_standard
from cfnlint.context.context import Parameter
from cfnlint.helpers import FUNCTIONS, FUNCTIONS_SINGLE, REGIONS, ToPy
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V
from cfnlint.jsonschema._utils import ensure_list

_singular_types = ["boolean", "integer", "number", "string"]
_all_types = ["array", "boolean", "integer", "number", "object", "string"]


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


class Scalar:
    def __init__(self) -> None:
        self.types = ["string"]
        self.supported_functions = []

    def schema_function(self) -> Iterator[ValidationError]:
        return {
            "type": self.types,
        }

    def is_valid(
        self,
        validator: Validator,
        instance: Any,
    ) -> Iterator[ValidationError]:
        ff = validator.function_filter.evolve(functions=self.supported_functions)
        v = validator.evolve(function_filter=ff)
        try:
            err = next(v.descend(instance, self.schema_function(), None, None))
            yield err
        except StopIteration:
            pass


class Fn(Scalar):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.fn = ToPy(name)
        self.supported_types = _singular_types

    def value(self, instance: Dict[str, Any]) -> Any:
        return instance.get(self.fn.name)

    def descend(
        self,
        validator: Validator,
        instance: Any,
        schema: Any,
        path: Deque | None = None,
    ) -> Iterator[ValidationError]:
        for err in validator.descend(instance, schema, path):
            err.path.appendleft(self.fn.name)
            if err.validator not in cfn_validators:
                err.validator = self.fn.py
            yield err

    def is_valid(
        self,
        validator: Validator,
        instance: Any,
    ) -> Iterator[ValidationError]:
        tS = ensure_list(validator.schema.get("type"))
        if tS:
            for t in tS:
                if t in self.supported_types:
                    break
            else:
                reprs = ", ".join(repr(type) for type in self.supported_types)
                yield ValidationError(f"{instance!r} is not of type {reprs}")
        if not validator.is_type(instance, "object"):
            return

        value = instance.get(self.fn.name)
        try:
            err = next(super().is_valid(validator, value))
            err.validator = self.fn.py
            yield err
        except StopIteration:
            pass


class FnArray:
    def __init__(self, name: str, min_length: int = 0, max_length: int = 0) -> None:
        self.fn = ToPy(name)
        self._min_length = min_length
        self._max_length = max_length
        self.items: Sequence[Scalar] = []
        self.supported_types = ["array"]

    def value(self, instance: Dict[str, Any]) -> Any:
        return instance.get(self.fn.name)

    def schema_function(self) -> Iterator[ValidationError]:
        schema = {
            "type": "array",
        }
        if not self._min_length:
            schema["minItems"] = self._min_length

        if not self._max_length:
            schema["maxItems"] = self._max_length
        return schema

    def descend(
        self,
        validator: Validator,
        instance: Any,
        schema: Any,
        path: Deque | None = None,
    ) -> Iterator[ValidationError]:
        for err in validator.descend(instance, schema, path):
            err.path.appendleft(self.fn.name)
            if err.validator not in cfn_validators:
                err.validator = self.fn.py
            yield err

    def is_valid(
        self,
        validator: Validator,
        instance: Any,
    ) -> Iterator[ValidationError]:
        tS = ensure_list(validator.schema.get("type"))
        if tS:
            for t in tS:
                if t in self.supported_types:
                    break
            else:
                reprs = ", ".join(repr(type) for type in self.supported_types)
                yield ValidationError(f"{instance!r} is not of type {reprs}")

        if not validator.is_type(instance, "object"):
            return

        value = instance.get(self.fn.name)

        try:
            err = next(self.descend(validator, value, self.schema_function(), None))
            yield err
        except StopIteration:
            pass

        for i in range(0, self._max_length):
            try:
                err = next(self.items[i].is_valid(validator, value[i]))
                err.validator = self.fn.py
                yield err
            except (IndexError, StopIteration):
                pass


class Ref(Fn):
    def __init__(self) -> None:
        super().__init__("Ref")
        self.supported_types = ["array"] + _singular_types

    def ref(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        if validator.context.transforms.has_language_extensions_transform():
            self.supported_functions.append("Ref")

        for err in self.is_valid(validator, instance):
            yield err
            return

        value = self.value(instance)
        if validator.is_type(value, "string"):
            for err in self.descend(
                validator, value, {"enum": validator.context.refs}, None
            ):
                yield err
                return

        # if the ref is to pseudo-parameter or parameter we can validate the values
        if value in validator.context.other_refs:
            for err in self.descend(
                validator, value, validator.context.parameters[value], None
            ):
                yield err
                return
        elif value in validator.context.parameters:
            default = validator.context.parameters[value].default
            if default:
                ctx = validator.context.evolve(
                    value_path=deque(["Parameters", value, "Default"])
                )
                v = validator.evolve(context=ctx)
                yield from v.descend(default, s, self.fn.name, None)

            allowed_values = validator.context.parameters[value].allowed_values
            if allowed_values:
                for i, allowed_value in enumerate(allowed_values):
                    ctx = validator.context.evolve(
                        value_path=deque(["Parameters", value, "AllowedValues", i])
                    )
                    v = validator.evolve(context=ctx)
                    yield from v.descend(allowed_value, s, self.fn.name, None)


class FnGetAtt(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::GetAtt")
        self.types = ["array", "string"]
        self.schema_array = {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": [
                {"type": "string"},
                {"type": "string"},
            ],
        }
        self.validator_resource = Scalar()
        self.validator_attribute = Scalar()
        self.supported_types = _all_types

    def get_att(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        if validator.context.transforms.has_language_extensions_transform():
            self.supported_functions.append("Ref")

        for err in self.is_valid(validator, instance):
            yield err
            return

        value = self.value(instance)
        paths = [0, 1]
        if validator.is_type(value, "string"):
            paths = [None, None]
            value = value.split(".", 1)

        for err in self.descend(
            validator,
            value[0],
            {"enum": list(validator.context.resources.keys())},
            paths[0],
        ):
            yield err
            return

        if all(
            not (bool(re.match(each, value[1])))
            for each in validator.context.resources[value[0]].get_atts
        ):
            yield ValidationError(
                f"{value[1]!r} is not one of {validator.context.resources[value[0]].get_atts!r}",
                validator=self.fn.py,
                path=deque([self.fn.name, 1]),
            )


class FnBase64(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Base64")
        self.supported_functions = FUNCTIONS_SINGLE
        self.supported_types = ["string"]

    def base64(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        yield from self.is_valid(validator, instance)


class FnGetAZs(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::GetAZs")
        self.supported_functions = ["Ref"]
        self.supported_types = ["array"]

    def get_azs(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        yield from self.is_valid(validator, instance)

        value = self.value(instance)
        if validator.is_type(value, "string"):
            # value can be empty which is equivalent {"Ref": "AWS::NoValue"}
            if value != "":
                yield from self.descend(validator, value, {"enum": REGIONS}, None)
            return

        valid_refs = ["AWS::Region"].extend(list(validator.context.parameters.keys()))
        yield from self.descend(validator, value, {"enum": valid_refs}, None)


class FnImportalue(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::ImportValue")
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
        yield from self.is_valid(validator, instance)


class FnJoin(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Join", 2, 2)
        self.items.append(Scalar())
        values = Scalar()
        values.types = ["array"]
        values.supported_functions.extend(
            [
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Split",
                "Ref",
            ]
        )
        self.supported_types = ["string"]
        self.items.append(values)

    def join(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return

        # we have to validate the second element manually
        values = instance.get(self.fn.name)[1]

        if validator.is_type(values, "array"):
            for value in values:
                scalar = Scalar()
                scalar.supported_functions = [
                    "Fn::Base64",
                    "Fn::FindInMap",
                    "Fn::GetAtt",
                    "Fn::If",
                    "Fn::ImportValue",
                    "Fn::Join",
                    "Fn::Select",
                    "Fn::Sub",
                    "Fn::Transform",
                    "Ref",
                ]

                for err in scalar.is_valid(validator, value):
                    yield err
                    return


class FnSplit(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Split", 2, 2)
        self.items.append(Scalar())
        s = Scalar()
        s.supported_functions.extend(
            [
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::GetAtt",
                "Fn::GetAZs",
                "Fn::If",
                "Fn::ImportValue",
                "Fn::Join",
                "Fn::Select",
                "Fn::Sub",
                "Ref",
            ]
        )
        self.items.append(s)

    def split(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return


class FnFindInMap(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::FindInMap", 3, 3)
        s = Scalar()
        s.supported_functions.extend(
            [
                "Fn::FindInMap",
                "Ref",
            ]
        )
        self.supported_types = ["array"] + _singular_types
        self.items.extend([s, s, s])

    def find_in_map(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return


class FnSelect(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Select", 2, 2)
        index = Scalar()
        index.supported_functions.extend(["Ref", "Fn::FindInMap"])
        self.supported_types = ["array", "object"] + _singular_types
        self.items.append(index)
        values = Scalar()
        values.types = ["array"]
        values.supported_functions.extend(
            [
                "Fn::FindInMap",
                "Fn::GetAtt",
                "Fn::GetAZs",
                "Fn::If",
                "Fn::Split",
                "Fn::Cidr",
                "Ref",
            ]
        )
        self.items.append(values)

    def select(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return

        # we have to validate the second element manually
        values = instance.get(self.fn.name)[1]

        if validator.is_type(values, "array"):
            scalar = Scalar()
            scalar.supported_functions = [
                "Fn::FindInMap",
                "Fn::GetAtt",
                "Fn::If",
                "Ref",
            ]
            for value in values:
                for err in scalar.is_valid(validator, value):
                    yield err
                    return


class FnIf(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::If", 3, 3)
        s = Scalar()
        s.supported_functions = FUNCTIONS
        self.items.extend([s])
        self.supported_types = _all_types

    def if_(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return

        value = self.value(instance)
        for i in [1, 2]:
            yield from self.descend(validator, value[i], s, i)


class FnSub(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Sub")
        self.types = ["array", "string"]
        self.schema_array = {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": [
                {"type": "string"},
                {"type": "object"},
            ],
        }

        self.validator_var = Scalar()
        self.validator_var.supported_functions = [
            "Fn::Base64",
            "Fn::FindInMap",
            "Fn::GetAZs",
            "Fn::GetAtt",
            "Fn::If",
            "Fn::ImportValue",
            "Fn::Join",
            "Fn::Select",
            "Fn::Sub",
            "Ref",
            "Fn::ToJsonString",
        ]

    def _validate_string(
        self, validator: Validator, instance: Any
    ) -> Iterator[ValidationError]:
        params = re.findall(r"\${([^}]+)}", instance)
        for param in params:
            param = param.strip()
            if param in validator.context.refs:
                continue
            yield ValidationError(
                message=f"Parameter {param!r} is not defined",
                validator=self.fn.py,
                path=deque([self.fn.name]),
            )

    def sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return

        value = self.value(instance)
        if validator.is_type(value, "array"):
            # we have to manually validate for this function
            for err in self.descend(
                validator,
                value,
                self.schema_array,
            ):
                yield err
                return

            keys = []

            errs = 0
            for k, v in value[1].items():
                keys.append(k)
                for err in self.validator_var.is_valid(
                    validator,
                    v,
                ):
                    err.path.extendleft([k, 1, self.fn.name])
                    yield err
                    errs += 1
            if errs > 0:
                return

            validator = validator.evolve(
                context=validator.context.evolve(
                    other_refs=dict.fromkeys(keys, Parameter({"Type": "String"}))
                )
            )
            value = value[0]

        yield from self._validate_string(validator, value)


class FnCidr(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Cidr", 2, 3)
        s = Scalar()
        s.supported_functions = [
            "Fn::FindInMap",
            "Fn::Select",
            "Ref",
            "Fn::GetAtt",
            "Fn::Sub",
            "Fn::ImportValue",
        ]
        self.items.extend([s, s, s])

    def cidr(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        yield from self.is_valid(validator, instance)


class FnLength(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Length")
        values = Scalar()
        values.supported_functions.extend(
            ["Ref", "Fn::FindInMap", "Fn::Split", "Fn::If"]
        )
        self.items.append(values)

    def length(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return

        # we have to validate the second element manually
        values = instance.get(self.fn.name)
        if validator.is_type(values, "array"):
            scalar = Scalar()
            scalar.supported_functions = [
                "Fn::If",
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::Join",
                "Fn::Select",
                "Fn::Sub",
                "Fn::ToJsonString",
                "Ref",
            ]
            for value in values:
                for err in scalar.is_valid(validator, value):
                    yield err
                    return


class FnToJsonString(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::ToJsonString")
        values = Scalar()
        values.supported_functions.extend(FUNCTIONS)
        self.items.append(values)

    def to_json_string(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        for err in self.is_valid(validator, instance):
            yield err
            return

        # we have to validate the second element manually
        values = instance.get(self.fn.name)
        if validator.is_type(values, "array"):
            scalar = Scalar()
            scalar.supported_functions = FUNCTIONS
            for value in values:
                for err in scalar.is_valid(validator, value):
                    yield err
                    return


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
    "fn_cidr": FnCidr().cidr,
    "fn_if": FnIf().if_,
    "fn_findinmap": FnFindInMap().find_in_map,
    "fn_getatt": FnGetAtt().get_att,
    "fn_getazs": FnGetAZs().get_azs,
    "fn_importvalue": FnImportalue().import_value,
    "fn_join": FnJoin().join,
    "fn_length": FnLength().length,
    "fn_select": FnSelect().select,
    "fn_split": FnSplit().split,
    "fn_sub": FnSub().sub,
    "fn_tojsonstring": FnToJsonString().to_json_string,
}
