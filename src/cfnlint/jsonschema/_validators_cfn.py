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

import json
from collections import deque
from typing import Any, Dict, List, Tuple

import regex as re

import cfnlint.jsonschema._validators as validators_standard
from cfnlint.context.context import Parameter
from cfnlint.data.schemas.other import resources
from cfnlint.helpers import (
    FUNCTIONS_SINGLE,
    REGEX_DYN_REF,
    REGEX_SUB_PARAMETERS,
    REGIONS,
    VALID_PARAMETER_TYPES,
    VALID_PARAMETER_TYPES_LIST,
    ToPy,
    load_resource,
)
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


def tagging(validator: Validator, t: Any, instance: Any, schema: Any):
    if not t.get("taggable"):
        return
    schema = load_resource(resources, "tagging.json")
    for err in validator.descend(
        instance,
        schema,
    ):
        err.validator = "tagging"
        yield err


class _Fn:
    def __init__(self, name: str, types: List[str], functions: List[str]) -> None:
        self.fn = ToPy(name)
        self.types = types
        self.functions = functions

    def _key_value(self, instance: Dict[str, Any]) -> Tuple[str, Any]:
        return list(instance.keys())[0], instance.get(self.fn.name)

    def _fix_errors(self, errs: ValidationResult) -> ValidationResult:
        for err in errs:
            if err.validator not in cfn_validators:
                err.validator = self.fn.py
            yield err

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["string"],
        }

    def _validator(self, validator: Validator) -> Validator:
        return validator.evolve(
            context=validator.context.evolve(functions=self.functions),
        )

    def resolve(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        key, _ = self._key_value(instance)

        for value, v, resolve_err in validator.resolve_value(instance):
            if resolve_err:
                yield resolve_err
                continue
            for err in self._fix_errors(v.descend(value, s, key)):
                err.message = err.message.replace(f"{value!r}", f"{instance!r}")
                err.message = f"{err.message} when {self.fn.name!r} is resolved"
                yield err

    def validate(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        # validate this function will return the correct type
        errs = list(_validate_fn_output_types(validator, s, instance, self.types))

        key, value = self._key_value(instance)
        errs.extend(
            list(
                self._fix_errors(
                    self._validator(validator).descend(
                        value, self.schema(validator, instance), path=key
                    )
                )
            )
        )

        if errs:
            yield from iter(errs)
            return

        yield from self.resolve(validator, s, instance, schema)


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
                        functions=subschema.get("functions", [])
                    ),
                ).descend(
                    instance=item,
                    schema=subschema.get("schema", {}),
                    path=index,
                )
        else:
            for index, item in enumerate(instance):
                yield from validator.evolve(
                    context=validator.context.evolve(functions=s.get("functions", [])),
                ).descend(
                    instance=item,
                    schema=s.get("schema", {}),
                    path=index,
                )


class FnGetAtt(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::GetAtt", _all_types, [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        resource_functions = []
        if validator.context.transforms.has_language_extensions_transform():
            resource_functions = ["Ref"]

        return {
            "type": ["string", "array"],
            "minItems": 2,
            "maxItems": 2,
            "fn_items": [
                {
                    "functions": resource_functions,
                    "schema": {
                        "type": ["string"],
                    },
                },
                {
                    "functions": ["Ref"],
                    "schema": {
                        "type": ["string"],
                    },
                },
            ],
        }

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        key, value = self._key_value(instance)
        paths: List[int | None] = [0, 1]
        if validator.is_type(value, "string"):
            paths = [None, None]
            value = value.split(".", 1)

        for err in validator.descend(
            value[0],
            {"enum": list(validator.context.resources.keys())},
            key,
        ):
            err.path.appendleft(paths[0])
            yield err
            return

        if not (
            validator.is_type(value[0], "string")
            and validator.is_type(value[1], "string")
        ):
            return
        if all(
            not (bool(re.fullmatch(each, value[1])))
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
            return

        # because of the complexities of schemas ($ref, anyOf, allOf, etc.)
        # we will simplify the validator to just have a type check
        # then we will provide a simple value to represent the type from the
        # getAtt
        evolved = validator.evolve()  # type: ignore
        evolved.validators = {  # type: ignore
            "type": validator.validators.get("type"),  # type: ignore
        }

        def iter_errors(type: str) -> ValidationResult:
            value: Any = None
            if type == "string":
                value = ""
            elif type == "number":
                value = 1.0
            elif type == "integer":
                value = 1
            elif type == "boolean":
                value = True
            elif type == "array":
                value = []
            elif type == "object":
                value = {}
            else:
                return

            for err in evolved.iter_errors(value):
                err.message = err.message.replace(f"{value!r}", f"{instance!r}")
                yield err

        types = ensure_list(
            validator.context.resources[value[0]].get_atts[value[1]].type
        )

        # validate all possible types.  We will only alert when all types fail
        type_err_ct = 0
        all_errs = []
        for type in types:
            errs = list(iter_errors(type))
            if errs:
                type_err_ct += 1
                all_errs.extend(errs)

        if type_err_ct == len(types):
            yield from errs


class Ref(_Fn):
    def __init__(self) -> None:
        super().__init__("Ref", _all_types, [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["string"],
            "enum": validator.context.refs,
        }

    def _validator(self, validator: Validator) -> Validator:
        if validator.context.transforms.has_language_extensions_transform():
            supported_functions = [
                "Ref",
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Sub",
                "Fn::ToJsonString",
            ]
        else:
            supported_functions = []
        return validator.evolve(
            context=validator.context.evolve(
                path=self.fn.name,
                functions=supported_functions,
            ),
        )

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from super().validate(validator, s, instance, schema)

        _, value = self._key_value(instance)
        if not validator.is_type(value, "string"):
            return

        if value not in validator.context.parameters:
            return

        parameter_type = validator.context.parameters[value].type
        schema_types = _resolve_type(validator, s)
        if not schema_types:
            return
        reprs = ", ".join(repr(type) for type in schema_types)

        if all(
            st not in ["string", "boolean", "integer", "number"] for st in schema_types
        ):
            if parameter_type not in VALID_PARAMETER_TYPES_LIST:
                yield ValidationError(f"{instance!r} is not of type {reprs}")
        elif all(st not in ["array"] for st in schema_types):
            if parameter_type not in [
                x for x in VALID_PARAMETER_TYPES if x not in VALID_PARAMETER_TYPES_LIST
            ]:
                yield ValidationError(f"{instance!r} is not of type {reprs}")


class FnGetAZs(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::GetAZs", ["array"], ["Ref"])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["string"],
            "enum": [""] + REGIONS,
        }


class FnImportValue(_Fn):
    def __init__(self) -> None:
        super().__init__(
            "Fn::ImportValue",
            _singular_types,
            [
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Select",
                "Fn::Sub",
                "Ref",
            ],
        )

    def _validator(self, validator: Validator) -> Validator:
        return validator.evolve(
            context=validator.context.evolve(
                path=self.fn.name,
                functions=self.functions,
                resources={},
            ),
        )


class FnBase64(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Base64", ["string"], list(FUNCTIONS_SINGLE))


class FnJoin(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Join", ["string"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": [
                {
                    "schema": {
                        "type": ["string"],
                    },
                },
                {
                    "functions": [
                        "Fn::FindInMap",
                        "Fn::If",
                        "Fn::Split",
                        "Ref",
                    ],
                    "schema": {
                        "type": ["array"],
                        "fn_items": {
                            "functions": [
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
                            ],
                            "schema": {
                                "type": ["string"],
                            },
                        },
                    },
                },
            ],
        }


class FnSplit(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Split", ["array"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": [
                {
                    "schema": {
                        "type": ["string"],
                    }
                },
                {
                    "functions": [
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
                    ],
                    "schema": {
                        "type": ["string"],
                    },
                },
            ],
        }

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        key, value = self._key_value(instance)
        if re.fullmatch(REGEX_DYN_REF, json.dumps(value[1])):
            yield ValidationError(
                f"{self.fn.name} does not support dynamic references",
                validator=self.fn.name,
                path=[key, 1],
            )


class FnFindInMap(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::FindInMap", ["array"] + _singular_types, [])
        self.scalar_schema = {
            "functions": [
                "Fn::FindInMap",
                "Ref",
            ],
            "schema": {
                "type": ["string"],
            },
        }

    def schema(self, validator: Validator, instance: Any) -> Dict[str, Any]:
        scalar_schema = {
            "functions": [
                "Fn::FindInMap",
                "Ref",
            ],
            "schema": {
                "type": ["string"],
            },
        }

        schema = {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "fn_items": [
                scalar_schema,
                scalar_schema,
                scalar_schema,
            ],
        }

        if validator.context.transforms.has_language_extensions_transform():
            schema["maxItems"] = 4
            schema["fn_items"] = [
                scalar_schema,
                scalar_schema,
                scalar_schema,
                {
                    "schema": {
                        "type": ["object"],
                        "properties": {
                            "DefaultValue": {
                                "type": ["array"] + _singular_types,
                            }
                        },
                        "additionalProperties": False,
                        "required": ["DefaultValue"],
                    }
                },
            ]

        return schema


class FnSelect(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Select", _all_types, [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": [
                {
                    "functions": ["Ref", "Fn::FindInMap"],
                    "schema": {
                        "type": ["integer"],
                    },
                },
                {
                    "functions": [
                        "Fn::FindInMap",
                        "Fn::GetAtt",
                        "Fn::GetAZs",
                        "Fn::If",
                        "Fn::Split",
                        "Fn::Cidr",
                        "Ref",
                    ],
                    "schema": {
                        "type": ["array"],
                        "fn_items": {
                            "functions": [
                                "Fn::FindInMap",
                                "Fn::GetAtt",
                                "Fn::If",
                                "Ref",
                            ],
                            "schema": {
                                "type": _all_types,
                            },
                        },
                    },
                },
            ],
        }


class FnIf(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::If", _all_types, [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["array"],
            "minItems": 3,
            "maxItems": 3,
            "fn_items": [
                {
                    "schema": {
                        "type": ["string"],
                    }
                },
            ],
        }

    def resolve(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        key, _ = self._key_value(instance)
        for value, v, _ in validator.resolve_value(instance):
            for err in v.descend(value, s, key):
                err.path.extend(v.context.value_path)
                yield err


class FnSub(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Sub", ["string"], [])
        self.sub_parameter_types = ["string", "integer", "number", "boolean"]

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["array", "string"],
            "minItems": 2,
            "maxItems": 2,
            "fn_items": [
                {
                    "schema": {"type": "string"},
                },
                {
                    "functions": [
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
                    ],
                    "schema": {
                        "type": ["object"],
                        "patternProperties": {
                            "[a-zA-Z0-9]+": {
                                "type": ["string"],
                            }
                        },
                        "additionalProperties": False,
                    },
                },
            ],
        }

    def _validate_string(self, validator: Validator, instance: Any) -> ValidationResult:
        params = re.findall(REGEX_SUB_PARAMETERS, instance)
        for param in params:
            if param.startswith("!"):
                continue
            param = param.strip()
            valid_params = []
            if "." in param:
                [name, attr] = param.split(".", 1)
                if name in validator.context.resources:
                    if attr in validator.context.resources[name].get_atts:
                        tS = ensure_list(
                            validator.context.resources[name].get_atts[attr].type
                        )
                        if not any(type in tS for type in self.sub_parameter_types):
                            reprs = ", ".join(
                                repr(type) for type in self.sub_parameter_types
                            )
                            yield ValidationError(
                                message=f"{param!r} is not of type {reprs}",
                                validator=self.fn.py,
                                path=deque([self.fn.name]),
                            )
                            continue
                    valid_params = [
                        f"{name}.{attr}"
                        for attr in list(
                            validator.context.resources[name].get_atts.keys()
                        )
                    ]
                else:
                    valid_params = list(validator.context.resources.keys())
            else:
                valid_params = validator.context.refs

            if param not in valid_params:
                yield ValidationError(
                    message=f"{param!r} is not one of {valid_params!r}",
                    validator=self.fn.py,
                    path=deque([self.fn.name]),
                )

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from super().validate(validator, s, instance, schema)

        _, value = self._key_value(instance)
        if validator.is_type(value, "array"):
            if len(value) != 2:
                return
            if not validator.is_type(value[1], "object"):
                return

            validator_string = validator.evolve(
                context=validator.context.evolve(
                    ref_values=dict.fromkeys(
                        list(value[1].keys()), Parameter({"Type": "String"})
                    ),
                )
            )
            value = value[0]
        elif validator.is_type(value, "string"):
            validator_string = validator
        else:
            return

        yield from self._validate_string(validator_string, value)


class FnCidr(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Cidr", ["array"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        functions = [
            "Fn::FindInMap",
            "Fn::Select",
            "Ref",
            "Fn::GetAtt",
            "Fn::Sub",
            "Fn::ImportValue",
            "Fn::If",
        ]
        return {
            "type": ["array"],
            "maxItems": 3,
            "minItems": 2,
            "fn_items": [
                {
                    "functions": functions,
                    "schema": {
                        "type": ["string"],
                        "pattern": (
                            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.)"
                            "{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                            "(\\/([0-9]|[1-2][0-9]|3[0-2]))$"
                        ),
                    },
                },
                {
                    "functions": functions,
                    "schema": {
                        "type": ["integer"],
                        "minimum": 1,
                        "maximum": 256,
                    },
                },
                {
                    "functions": functions,
                    "schema": {
                        "type": ["integer"],
                        "minimum": 1,
                        "maximum": 128,
                    },
                },
            ],
        }


class FnLength(_Fn):
    def __init__(self) -> None:
        super().__init__(
            "Fn::Length",
            ["integer"],
            [
                "Ref",
                "Fn::FindInMap",
                "Fn::Split",
                "Fn::If",
                "Fn::GetAZs",
            ],
        )

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["array"],
            "fn_items": {
                "functions": [
                    "Fn::If",
                    "Fn::Base64",
                    "Fn::FindInMap",
                    "Fn::Join",
                    "Fn::Select",
                    "Fn::Split",
                    "Fn::Sub",
                    "Fn::ToJsonString",
                    "Fn::GetAZs",
                    "Ref",
                ],
                "schema": {
                    "type": _all_types,
                },
            },
        }

    def validate(
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

        yield from super().validate(validator, s, instance, schema)


class FnToJsonString(_Fn):
    def __init__(self) -> None:
        super().__init__(
            "Fn::ToJsonString",
            ["string"],
            [],
        )

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["array", "object"],
        }

    def validate(
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

        yield from super().validate(validator, s, instance, schema)


class FnForEach(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::ForEach", ["object"], [])

    def _key_value(self, instance: Dict[str, Any]) -> Tuple[str, Any]:
        for key, value in instance.items():
            if key.startswith(self.fn.name):
                return key, value

        return super()._key_value(instance)

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["array"],
            "minItems": 3,
            "maxItems": 3,
            "fn_items": [
                {
                    "functions": [
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
                    ],
                    "schema": {
                        "type": ["string"],
                    },
                },
                {
                    "functions": [
                        "Fn::FindInMap",
                        "Fn::GetAtt",
                        "Fn::GetAZs",
                        "Fn::Transform",
                        "Fn::Select",
                        "Fn::Sub",
                        "Fn::ToJsonString",
                        "Ref",
                    ],
                    "schema": {
                        "type": ["array"],
                        "fn_items": {
                            "functions": [
                                "Fn::FindInMap",
                                "Fn::GetAtt",
                                "Fn::Transform",
                                "Fn::Select",
                                "Fn::Sub",
                                "Fn::ToJsonString",
                                "Ref",
                            ],
                            "schema": {
                                "type": ["string"],
                            },
                        },
                    },
                },
                {
                    "schema": {
                        "type": ["object"],
                    }
                },
            ],
        }

    def resolve(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        return
        yield

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        key, _ = self._key_value(instance)
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{key} is not supported without "
                    "'AWS::LanguageExtensions' transform"
                )
            )
            return

        yield from super().validate(validator, s, instance, schema)


#####
# Condition functions
#####


class FnEquals(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Equals", ["boolean"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": {
                "functions": [
                    "Ref",
                    "Fn::FindInMap",
                    "Fn::Sub",
                    "Fn::Join",
                    "Fn::Select",
                    "Fn::Split",
                    "Fn::Length",
                    "Fn::ToJsonString",
                ],
                "schema": {
                    "type": ["string"],
                },
            },
        }


class FnOr(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Or", ["boolean"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "fn_items": {
                "functions": [
                    "Condition",
                    "Fn::Equals",
                    "Fn::Not",
                    "Fn::And",
                    "Fn::Or",
                ],
                "schema": {
                    "type": ["boolean"],
                },
            },
        }


class FnAnd(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::And", ["boolean"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "fn_items": {
                "functions": [
                    "Condition",
                    "Fn::Equals",
                    "Fn::Not",
                    "Fn::And",
                    "Fn::Or",
                ],
                "schema": {
                    "type": ["boolean"],
                },
            },
        }


class FnNot(_Fn):
    def __init__(self) -> None:
        super().__init__("Fn::Not", ["boolean"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 1,
            "minItems": 1,
            "fn_items": {
                "functions": [
                    "Condition",
                    "Fn::Equals",
                    "Fn::Not",
                    "Fn::And",
                    "Fn::Or",
                ],
                "schema": {
                    "type": ["boolean"],
                },
            },
        }


class Condition(_Fn):
    def __init__(self) -> None:
        super().__init__("Condition", ["boolean"], [])

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "string",
            "enum": validator.context.conditions,
        }


#####
# Type checks
#####
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
    "ref": Ref().validate,
    "fn_base64": FnBase64().validate,
    "fn_cidr": FnCidr().validate,
    "fn_if": FnIf().validate,
    "fn_findinmap": FnFindInMap().validate,
    "fn_foreach": FnForEach().validate,
    "fn_getatt": FnGetAtt().validate,
    "fn_getazs": FnGetAZs().validate,
    "fn_importvalue": FnImportValue().validate,
    "fn_join": FnJoin().validate,
    "fn_items": FnItems().validate,
    "fn_length": FnLength().validate,
    "fn_select": FnSelect().validate,
    "fn_split": FnSplit().validate,
    "fn_sub": FnSub().validate,
    "fn_tojsonstring": FnToJsonString().validate,
    "fn_equals": FnEquals().validate,
    "fn_or": FnOr().validate,
    "fn_and": FnAnd().validate,
    "fn_not": FnNot().validate,
    "condition": Condition().validate,
    "tagging": tagging,
}
