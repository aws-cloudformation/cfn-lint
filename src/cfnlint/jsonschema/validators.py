"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/validators.py
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from typing import Any, Deque, Dict, Iterator

from cfnlint.data.schemas.other import draft7
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import _validators, _validators_cfn
from cfnlint.jsonschema._context import Context
from cfnlint.jsonschema._filter import (
    FunctionFilter,
    cfn_function_filter,
    standard_function_filter,
)
from cfnlint.jsonschema._format import FormatChecker, cfn_format_checker
from cfnlint.jsonschema._resolver import RefResolver
from cfnlint.jsonschema._types import TypeChecker, cfn_type_checker
from cfnlint.jsonschema._typing import V
from cfnlint.jsonschema._utils import id_of
from cfnlint.jsonschema.exceptions import (
    UndefinedTypeCheck,
    UnknownType,
    ValidationError,
)
from cfnlint.template import Template

_meta_schema: Dict[str, Any] = load_resource(draft7, "schema.json")


def create(
    validators: Mapping[str, V] | None = None,
    function_filter: FunctionFilter | None = None,
):
    validators_arg = validators or {}
    function_filter_arg = function_filter or FunctionFilter([])

    @dataclass
    class Validator:
        """

        Arguments:

            schema:

                The schema that the validator object will validate with.
                It is assumed to be valid, and providing
                an invalid schema can lead to undefined behavior.
        """

        _meta_schema: Dict[str, Any] = field(
            init=False, default_factory=lambda: _meta_schema
        )
        _type_checker: TypeChecker = field(
            init=False, default_factory=lambda: cfn_type_checker
        )
        _format_checker: FormatChecker = field(
            init=False, default_factory=lambda: cfn_format_checker
        )

        #: The schema that will be used to validate instances
        schema: Mapping | bool = field(repr=True, default=True)
        validators: Mapping[str, V] = field(
            init=False, default_factory=lambda: validators_arg
        )
        resolver: RefResolver = field(default=None, repr=False)  # type: ignore
        function_filter: FunctionFilter = field(
            init=True, default_factory=lambda: function_filter_arg
        )
        cfn: Template | None = field(default=None)
        context: Context = field(default_factory=Context)

        def __post_init__(self):
            if self.function_filter is None:
                self.function_filter = cfn_function_filter
            if self.resolver is None:
                self.resolver = RefResolver.from_schema(
                    self.schema,
                )

        def is_type(self, instance: Any, type: str) -> bool:
            """
            Check if the instance is of the given (JSON Schema) type.

            Arguments:

                instance:

                    the value to check

                type:

                    the name of a known (JSON Schema) type

            Returns:

                whether the instance is of the given type

            Raises:

                `cfnlint.jsonschema.exceptions.UnknownType`:

                    if ``type`` is not a known type
            """
            try:
                return self._type_checker.is_type(instance, type)
            except UndefinedTypeCheck:
                raise UnknownType(type, instance, self.schema)

        def is_valid(self, instance: Any) -> bool:
            """
            Check if the instance is valid under the current `schema`.

            Returns:

                whether the instance is valid or not

            >>> schema = {"maxItems" : 2}
            >>> StandardValidator(schema).is_valid([2, 3, 4])
            False
            """
            error = next(self.iter_errors(instance), None)
            return error is None

        def iter_errors(self, instance: Any) -> Iterator[ValidationError]:
            r"""
            Lazily yield each of the validation errors in the given instance.

            >>> schema = {
            ...     "type" : "array",
            ...     "items" : {"enum" : [1, 2, 3]},
            ...     "maxItems" : 2,
            ... }
            >>> v = StandardValidator(schema)
            >>> for error in sorted(v.iter_errors([2, 3, 4]), key=str):
            ...     print(error.message)
            4 is not one of [1, 2, 3]
            [2, 3, 4] is too long
            """
            schema = self.schema

            if schema is True:
                return
            elif schema is False:
                yield ValidationError(
                    f"False schema does not allow {instance!r}",
                    validator=None,
                    validator_value=None,
                    instance=instance,
                    schema=schema,
                )
                return

            scope = id_of(schema)
            if scope:
                self.resolver.push_scope(scope)
            try:
                # we need filter and apply schemas against the new instances
                for _instance, _schema in self.function_filter.filter(
                    self, instance, schema
                ):
                    for k, v in _schema.items():
                        validator = self.validators.get(k)
                        if validator is None:
                            continue

                        errors = validator(self, v, instance, _schema) or ()
                        for error in errors:
                            # set details if not already set by the called fn
                            error._set(
                                validator=k,
                                validator_value=v,
                                instance=_instance,
                                schema=_schema,
                                type_checker=self._type_checker,
                            )
                            if k not in {"if", "$ref"}:
                                error.schema_path.appendleft(k)
                            yield error
            finally:
                if scope:
                    self.resolver.pop_scope()

        def validate(self, instance: Any) -> None:
            """
            Check if the instance is valid under the current `schema`.

            Raises:

                `cfnlint.jsonschema.exceptions.ValidationError`:

                    if the instance is invalid

            >>> schema = {"maxItems" : 2}
            >>> StandardValidator(schema).validate([2, 3, 4])
            Traceback (most recent call last):
                ...
            ValidationError: [2, 3, 4] is too long
            """
            for error in self.iter_errors(instance):
                raise error

        def descend(
            self,
            instance: Any,
            schema: Any,
            path: Deque | None = None,
            schema_path: Deque | None = None,
        ) -> Iterator[ValidationError]:
            if schema is True:
                return
            elif schema is False:
                yield ValidationError(
                    f"False schema does not allow {instance!r}",
                    validator=None,
                    validator_value=None,
                    instance=instance,
                    schema=schema,
                )
                return

            for error in self.evolve(schema=schema).iter_errors(instance):
                if path is not None:
                    error.path.appendleft(path)
                if schema_path is not None:
                    error.schema_path.appendleft(schema_path)
                yield error

        def evolve(self, **kwargs) -> "Validator":
            """
            Create a new validator like this one, but with given changes.

            Preserves all other attributes, so can be used to e.g. create a
            validator with a different schema but with the same :kw:`$ref`
            resolution behavior.

            >>> validator = StandardValidator({})
            >>> validator.evolve(schema={"type": "number"})
            StandardValidator(schema={'type': 'number'}, format_checker=None)
            """
            cls = self.__class__
            for f in fields(Validator):
                if f.init:
                    kwargs.setdefault(f.name, getattr(self, f.name))

            return cls(**kwargs)

        def extend(
            self,
            validators: Dict[str, V] | None = None,
            function_filter: FunctionFilter | None = None,
        ) -> "Validator":
            """
            Extends the current validator.

            Updates VALIDATORS in the current instance with the validators provided.

            >>> validator = StandardValidator({}).extend(validators={"type": type})
            """
            all_validators = dict(self.validators)
            if validators is not None:
                all_validators.update(validators)

            if function_filter is None:
                function_filter = self.function_filter

            return create(  # type: ignore
                validators=all_validators,
                function_filter=function_filter,
            )

    return Validator


_standard_validators: Dict[str, V] = {
    "$ref": _validators.ref,
    "additionalProperties": _validators.additionalProperties,
    "allOf": _validators.allOf,
    "anyOf": _validators.anyOf,
    "const": _validators.const,
    "contains": _validators.contains,
    "dependencies": _validators.dependencies,
    "enum": _validators.enum,
    "exclusiveMaximum": _validators.exclusiveMaximum,
    "exclusiveMinimum": _validators.exclusiveMinimum,
    "format": _validators.format,
    "if": _validators.if_,
    "items": _validators.items,
    "maxItems": _validators.maxItems,
    "maxLength": _validators.maxLength,
    "maxProperties": _validators.maxProperties,
    "maximum": _validators.maximum,
    "minItems": _validators.minItems,
    "minLength": _validators.minLength,
    "minProperties": _validators.minProperties,
    "minimum": _validators.minimum,
    "multipleOf": _validators.multipleOf,
    "not": _validators.not_,
    "oneOf": _validators.oneOf,
    "pattern": _validators.pattern,
    "patternProperties": _validators.patternProperties,
    "properties": _validators.properties,
    "propertyNames": _validators.propertyNames,
    "required": _validators.required,
    "type": _validators.type,
    "uniqueItems": _validators.uniqueItems,
}

CfnTemplateValidator = create(
    validators={
        **_standard_validators,
        **_validators_cfn.cfn_validators,
    },
    function_filter=cfn_function_filter,
)

StandardValidator = create(
    validators=_standard_validators,
    function_filter=standard_function_filter,
)
