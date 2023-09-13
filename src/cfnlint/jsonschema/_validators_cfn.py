"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from typing import Any, Dict, Iterator, List

import regex as re

import cfnlint.jsonschema._validators as validators_standard
from cfnlint.context.context import Parameter
from cfnlint.helpers import FUNCTIONS, FUNCTIONS_SINGLE, REGIONS, ToPy
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V, ValidationResult
from cfnlint.jsonschema._utils import ensure_list

_singular_types = ["boolean", "integer", "number", "string"]
_all_types = ["array", "boolean", "integer", "number", "object", "string"]


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


def _resolve_type(validator, schema):
    if "type" in schema:
        return ensure_list(schema["type"])

    if "$ref" in schema:
        resolve = getattr(validator.resolver, "resolve", None)
        ref = schema["$ref"]
        if resolve is None:
            resolved = validator.resolver.resolving(ref)
        else:
            _, resolved = validator.resolver.resolve(ref)

        if "type" in resolved:
            return ensure_list(resolved["type"])

    return []


def _validate_fn_output_types(
    validator, s, instance, supported_types
) -> ValidationResult:
    tS = _resolve_type(validator, s)
    if tS:
        for t in tS:
            if t in supported_types:
                break
        else:
            reprs = ", ".join(repr(type) for type in tS)
            yield ValidationError(f"{instance!r} is not of type {reprs}")


class Scalar:
    def __init__(self) -> None:
        self.types: List[str] = ["string"]
        self.supported_functions: List[str] = []

    def schema(self, validator, instance) -> Dict[str, str | List[str] | int]:
        return {
            "type": self.types,
        }

    def iter_errors(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        context = validator.context.evolve(functions=self.supported_functions)
        v = validator.evolve(context=context)
        try:
            yield from v.descend(instance, self.schema(validator, instance), None, None)
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
        path: str | int | None = None,
    ) -> ValidationResult:
        validator = validator.evolve(
            context=validator.context.evolve(path=self.fn.name)
        )
        for err in validator.descend(instance, schema, path):
            if err.validator not in cfn_validators:
                err.validator = self.fn.py
            yield err

    def iter_errors(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        # validate this function will return the correct type
        yield from _validate_fn_output_types(
            validator, s, instance, self.supported_types
        )

        validator = validator.evolve(
            context=validator.context.evolve(
                path=self.fn.name, functions=self.supported_functions
            ),
        )

        key = list(instance.keys())[0]
        value = instance.get(self.fn.name)
        for err in validator.descend(value, self.schema(validator, instance), key):
            err.validator = self.fn.py
            yield err


class FnArray:
    def __init__(self, name: str, min_length: int = 0, max_length: int = 0) -> None:
        self.fn = ToPy(name)
        self._min_length = min_length
        self._max_length = max_length
        self.items: List[Scalar] = []
        self.supported_types = ["array"]

    def value(self, instance: Dict[str, Any]) -> Any:
        return instance.get(self.fn.name)

    def schema(self) -> Dict[str, str | int]:
        schema: Dict[str, str | int] = {
            "type": "array",
        }
        if self._min_length:
            schema["minItems"] = self._min_length

        if self._max_length:
            schema["maxItems"] = self._max_length
        return schema

    def descend(
        self,
        validator: Validator,
        instance: Any,
        schema: Any,
        path: str | int | None = None,
    ) -> ValidationResult:
        for err in validator.descend(instance, schema, path):
            if err.validator not in cfn_validators:
                err.validator = self.fn.py
            yield err

    def iter_errors(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        yield from _validate_fn_output_types(
            validator, s, instance, self.supported_types
        )

        if not validator.is_type(instance, "object"):
            return

        value = instance.get(self.fn.name)
        key = list(instance.keys())[0]
        yield from self.descend(validator, value, self.schema(), key)

        if not validator.is_type(value, "array"):
            return
        for i in range(0, self._max_length):
            try:
                for err in self.items[i].iter_errors(validator, s, value[i], schema):
                    err.path.appendleft(key)
                    err.validator = self.fn.py
                    yield err
            except (IndexError, StopIteration):
                pass


class Ref(Fn):
    def __init__(self) -> None:
        super().__init__("Ref")
        self.supported_types = ["array", "object"] + _singular_types
        self.types = ["string"]

    def ref_resolver(self, validator: Validator, instance: Any) -> Iterator[Any]:
        if validator.is_type(instance, "string"):
            # if the ref is to pseudo-parameter or parameter we can validate the values
            for possible_value in validator.context.ref_values[instance]:
                yield possible_value

    def ref(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if validator.context.transforms.has_language_extensions_transform():
            self.supported_functions = ["Ref"]
            self.types.append("object")

        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return

        value = instance.get(self.fn.name)
        key = list(instance.keys())[0]

        for err in self.descend(
            validator, value, {"enum": validator.context.refs}, self.fn.name
        ):
            yield err
            return

        print("Start", instance)
        for value in validator.resolve(instance):
            print("Value", value)


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
    ) -> ValidationResult:
        if validator.context.transforms.has_language_extensions_transform():
            self.supported_functions.append("Ref")

        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return

        value = self.value(instance)
        key = list(instance.keys())[0]
        paths: List[int | None] = [0, 1]
        if validator.is_type(value, "string"):
            paths = [None, None]
            value = value.split(".", 1)

        for err in self.descend(
            validator,
            value[0],
            {"enum": list(validator.context.resources.keys())},
            paths[0],
        ):
            err.path.appendleft(key)
            yield err
            return

        if not (
            validator.is_type(value[0], "string")
            and validator.is_type(value[1], "string")
        ):
            return
        if all(
            not (bool(re.match(each, value[1])))
            for each in validator.context.resources[value[0]].get_atts
        ):
            yield ValidationError(
                (
                    f"{value[1]!r} is not one of "
                    f"{validator.context.resources[value[0]].get_atts!r}"
                ),
                validator=self.fn.py,
                path=deque([self.fn.name, 1]),
            )


class FnBase64(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Base64")
        self.supported_functions = list(FUNCTIONS_SINGLE)
        self.supported_types = ["string"]

    def base64(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from self.iter_errors(validator, s, instance, schema)


class FnGetAZs(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::GetAZs")
        self.supported_functions = ["Ref"]
        self.supported_types = ["array"]

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["string"],
            "enum": [""] + REGIONS,
        }

    def get_azs(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from self.iter_errors(validator, s, instance, schema)


class FnImportValue(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::ImportValue")
        self.supported_functions.extend(
            [
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Select",
                "Fn::Sub",
                "Ref",
            ]
        )

    def import_value(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        validator = validator.evolve(
            context=validator.context.evolve(
                resources={},
            )
        )
        yield from self.iter_errors(validator, s, instance, schema)


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
    ) -> ValidationResult:
        for err in self.iter_errors(validator, s, instance, schema):
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

                for err in scalar.iter_errors(validator, s, value, schema):
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
    ) -> ValidationResult:
        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return


class _FindInMapDefault(Scalar):
    def __init__(self) -> None:
        super().__init__()
        self.types = ["object"]

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "types": ["object"],
            "properties": {
                "DefaultValue": {
                    "type": ["string", "array", "integer", "boolean"],
                }
            },
            "additionalProperties": False,
            "required": ["DefaultValue"],
        }


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
    ) -> ValidationResult:
        if validator.context.transforms.has_language_extensions_transform():
            self._max_length = 4
            self.items.append(_FindInMapDefault())

        for err in self.iter_errors(validator, s, instance, schema):
            yield err


class FnSelect(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Select", 2, 2)
        index = Scalar()
        index.types = ["integer"]
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
    ) -> ValidationResult:
        for err in self.iter_errors(validator, s, instance, schema):
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
                for err in scalar.iter_errors(validator, s, value, schema):
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
    ) -> ValidationResult:
        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return

        value = self.value(instance)
        key = list(instance.keys())[0]
        for i in [1, 2]:
            for err in self.descend(validator, value[i], s, i):
                err.path.appendleft(key)
                yield err


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

    def _validate_string(self, validator: Validator, instance: Any) -> ValidationResult:
        params = re.findall(r"\${([^}]+)}", instance)
        for param in params:
            if param.startswith("!"):
                continue
            param = param.strip()
            valid_params = []
            if "." in param:
                [name, attr] = param.split(".", 1)
                if name in validator.context.resources:
                    if attr in validator.context.resources[name].get_atts:
                        continue
                    valid_params = [
                        f"{name}.{attr}"
                        for attr in list(
                            validator.context.resources[name].get_atts.keys()
                        )
                    ]
                else:
                    valid_params = list(validator.context.resources.keys())
            elif param in validator.context.refs:
                continue
            else:
                valid_params = validator.context.refs
            yield ValidationError(
                message=f"{param!r} is not one of {valid_params!r}",
                validator=self.fn.py,
                path=deque([self.fn.name]),
            )

    def sub(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return

        value = self.value(instance)
        key = list(instance.keys())[0]
        if validator.is_type(value, "array"):
            # we have to manually validate for this function
            for err in self.descend(
                validator,
                value,
                self.schema_array,
            ):
                err.path.appendleft(key)
                yield err
                return

            keys = []

            errs = 0
            for k, v in value[1].items():
                keys.append(k)
                for err in self.validator_var.iter_errors(
                    validator,
                    s,
                    v,
                    schema,
                ):
                    err.path.appendleft([k, 1, self.fn.name])
                    yield err
                    errs += 1
            if errs > 0:
                return

            validator = validator.evolve(
                context=validator.context.evolve(
                    other_refs=dict.fromkeys(keys, Parameter({"Type": "String"})),
                    sub_parameters=dict.fromkeys(keys, Parameter({"Type": "String"})),
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
    ) -> ValidationResult:
        yield from self.iter_errors(validator, s, instance, schema)


class FnLength(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::Length")
        self.supported_types = ["integer"]
        values = Scalar()
        values.supported_functions.extend(
            ["Ref", "Fn::FindInMap", "Fn::Split", "Fn::If"]
        )
        self.items.append(values)

    def length(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{self.fn.name} is not supported without "
                    "'AWS::LanguageExtensions' transform"
                )
            )
            return
        for err in self.iter_errors(validator, s, instance, schema):
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
                for err in scalar.iter_errors(validator, s, value, schema):
                    yield err
                    return


class FnToJsonString(Fn):
    def __init__(self) -> None:
        super().__init__("Fn::ToJsonString")
        self.types = ["array", "object"]
        self.supported_types = ["string"]

    def to_json_string(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{self.fn.name} is not supported without "
                    "'AWS::LanguageExtensions' transform"
                )
            )
            return
        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return

        # we don't validate the elements inside a JsonString
        # as it can be anything


class FnForEach(FnArray):
    def __init__(self) -> None:
        super().__init__("Fn::ForEach", 3, 3)
        self.supported_types = ["object"]
        identifier = Scalar()
        identifier.supported_functions = [
            "Fn::Base64",
            "Fn::FindInMap",
            "Fn::GetAtt",
            "Fn::ImportValue",
            "Fn::Join",
            "Fn::Length",
            "Fn::Transform",
            "Fn::Select",
            "Fn::Sub",
            "Fn::ToJsonString",
            "Ref",
        ]
        self.items.append(identifier)
        collection = Scalar()
        collection.types = ["array"]
        collection.supported_functions = [
            "Fn::FindInMap",
            "Fn::GetAtt",
            "Fn::GetAZs",
            "Fn::Transform",
            "Fn::Select",
            "Fn::Sub",
            "Fn::ToJsonString",
            "Ref",
        ]
        self.items.append(collection)
        output = Scalar()
        output.types = ["object"]
        self.items.append(output)

    def for_each(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        key = list(instance.keys())[0]
        self.fn = ToPy(key)
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{self.fn.name} is not supported without "
                    "'AWS::LanguageExtensions' transform"
                )
            )
            return

        for err in self.iter_errors(validator, s, instance, schema):
            yield err
            return
        # update the context about parameters and descend
        values = instance.get(self.fn.name)
        identifier = values[0]
        collection = values[1]
        output = values[2]
        for iterator in collection:
            validator = validator.evolve(
                context=validator.context.evolve(
                    ref_values={
                        identifier: iterator,
                    }
                )
            )
            for err in validator.descend(output, s, self.fn.name):
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
    "fn_foreach": FnForEach().for_each,
    "fn_getatt": FnGetAtt().get_att,
    "fn_getazs": FnGetAZs().get_azs,
    "fn_importvalue": FnImportValue().import_value,
    "fn_join": FnJoin().join,
    "fn_length": FnLength().length,
    "fn_select": FnSelect().select,
    "fn_split": FnSplit().split,
    "fn_sub": FnSub().sub,
    "fn_tojsonstring": FnToJsonString().to_json_string,
}

# not all functions need to be resolved.  These functions
# allow us to pull up values from nested functions
# allowing us to test the possible values against the schema
fn_resolvers: Dict[str, V] = {
    "Ref": Ref().ref_resolver,
}
