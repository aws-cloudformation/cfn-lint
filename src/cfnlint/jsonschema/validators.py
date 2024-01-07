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

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from typing import Any, Callable, Deque, Dict, Iterator, Tuple

from cfnlint.context import Context
from cfnlint.jsonschema import _resolvers_cfn, _validators, _validators_cfn
from cfnlint.jsonschema._filter import FunctionFilter
from cfnlint.jsonschema._format import FormatChecker, cfn_format_checker
from cfnlint.jsonschema._resolver import RefResolver
from cfnlint.jsonschema._types import TypeChecker, cfn_type_checker
from cfnlint.jsonschema._typing import V, ValidationResult
from cfnlint.jsonschema._utils import custom_msg, id_of
from cfnlint.jsonschema.exceptions import (
    UndefinedTypeCheck,
    UnknownType,
    ValidationError,
)
from cfnlint.template import Template


def create(
    validators: Mapping[str, V] | None = None,
    function_filter: FunctionFilter | None = None,
    context: Context | None = None,
    fn_resolvers: Mapping[str, Any] | None = None,
):
    validators_arg = validators or {}
    function_filter_arg = function_filter or FunctionFilter()
    context_arg = context or Context()
    fn_resolvers_arg = fn_resolvers or {}

    @dataclass
    class Validator:
        """

        Arguments:

            schema:

                The schema that the validator object will validate with.
                It is assumed to be valid, and providing
                an invalid schema can lead to undefined behavior.
        """

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
        context: Context = field(default_factory=lambda: context_arg)

        fn_resolvers: Mapping[str, Callable[["Validator", Any], Any]] = field(
            init=False, default_factory=lambda: fn_resolvers_arg
        )

        def __post_init__(self):
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

        def resolve_value(
            self, instance: Any
        ) -> Iterator[Tuple[Any, Deque, ValidationError | None]]:
            if self.is_type(instance, "object"):
                if len(instance) == 1:
                    for k, v in instance.items():
                        if k in self.fn_resolvers:
                            for value, _, _ in self.resolve_value(v):
                                yield from self.fn_resolvers[k](self, value)
                            return

            yield instance, deque([]), None

        def iter_errors(self, instance: Any) -> ValidationResult:
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

                        for err in validator(self, v, _instance, _schema) or ():
                            msg = custom_msg(k, _schema) or err.message
                            if msg is not None:
                                err.message = msg
                            # set details if not already set by the called fn
                            err._set(
                                validator=k,
                                validator_value=v,
                                instance=_instance,
                                schema=_schema,
                                type_checker=self._type_checker,
                            )
                            if k not in {"if", "$ref"}:
                                err.schema_path.appendleft(k)
                            yield err
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
            path: str | int | None = None,
            schema_path: str | None = None,
        ) -> ValidationResult:
            for error in self.evolve(
                schema=schema,
                context=self.context.evolve(
                    path=path,
                ),
            ).iter_errors(instance):
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
            context: Context | None = None,
            fn_resolvers: Mapping[str, Callable[["Validator", Any], Any]] | None = None,
        ) -> "Validator":
            """
            Extends the current validator.

            Updates validator in the current instance with the validators provided.

            >>> validator = StandardValidator({}).extend(validators={"type": type})
            """
            all_validators = dict(self.validators)
            if validators is not None:
                all_validators.update(validators)

            if function_filter is None:
                function_filter = self.function_filter

            if context is None:
                context = self.context

            all_fn_resolvers = dict(self.fn_resolvers)
            if fn_resolvers is not None:
                all_fn_resolvers.update(fn_resolvers)

            return create(  # type: ignore
                validators=all_validators,
                function_filter=function_filter,
                context=context,
                fn_resolvers=all_fn_resolvers,
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
    "dependentExcluded": _validators.dependentExcluded,
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
    "requiredXor": _validators.requiredXor,
    "requiredOr": _validators.requiredOr,
    "type": _validators.type,
    "uniqueItems": _validators.uniqueItems,
    "uniqueKeys": _validators.uniqueKeys,
}

CfnTemplateValidator = create(
    validators={
        **_standard_validators,
        **_validators_cfn.cfn_validators,
    },
    function_filter=FunctionFilter(),
    fn_resolvers=_resolvers_cfn.fn_resolvers,
)

StandardValidator = create(
    validators=_standard_validators,
    function_filter=FunctionFilter(),
)
