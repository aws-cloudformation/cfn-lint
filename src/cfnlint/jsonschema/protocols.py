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
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Type, runtime_checkable

from cfnlint.jsonschema._filter import FunctionFilter

if TYPE_CHECKING:
    from cfnlint.context import Context
    from cfnlint.jsonschema._format import FormatChecker
    from cfnlint.jsonschema._typing import ResolutionResult, V, ValidationResult
    from cfnlint.schema.resolver import RefResolver
    from cfnlint.template import Template


@runtime_checkable
class Validator(Protocol):
    """
    The protocol to which all validator classes adhere.

    Arguments:

        schema:

            The schema that the validator object will validate with.
            It is assumed to be valid, and providing
            an invalid schema can lead to undefined behavior.
    """

    #: A mapping of validation keywords (`str`\s) to functions that
    #: validate the keyword with that name. For more information see
    #: `creating-validators`.
    validators: ClassVar[Mapping]
    format_checker: ClassVar[FormatChecker]

    #: The schema that will be used to validate instances
    schema: Mapping | bool
    resolver: RefResolver

    cfn: Template
    context: Context
    function_filter: FunctionFilter
    cfn_path: deque[str]

    def __init__(
        self,
        schema: Mapping | bool,
    ) -> None: ...

    @classmethod
    def check_schema(cls, schema: Mapping | bool) -> None:
        """
        Validate the given schema against the validator's `META_SCHEMA`.

        Raises:

            `cfnlint.jsonschema.exceptions.SchemaError`:

                if the schema is invalid
        """

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

    def is_valid(self, instance: Any) -> bool:
        """
        Check if the instance is valid under the current `schema`.

        Returns:

            whether the instance is valid or not

        >>> schema = {"maxItems" : 2}
        >>> CfnTemplateValidator(schema).is_valid([2, 3, 4])
        False
        """

    def descend(
        self,
        instance: Any,
        schema: Any,
        path: str | int | None = None,
        schema_path: str | int | None = None,
        property_path: str | int | None = None,
    ) -> ValidationResult:
        """
        Descend into the schema validating the schema for True/False.
        It will validate the schema against the instance and append the
        path and schema_path as needed.

        >>> schema = {
        ...     "type" : "array",
        ...     "items" : {"enum" : [1, 2, 3]},
        ...     "maxItems" : 2,
        ... }
        >>> v = CfnTemplateValidator(schema)
        >>> for error in v.descend([2, 3, 4], schema, path=deque(["a"])):
        ...     print(error.message)
        """

    def iter_errors(self, instance: Any) -> ValidationResult:
        r"""
        Lazily yield each of the validation errors in the given instance.

        >>> schema = {
        ...     "type" : "array",
        ...     "items" : {"enum" : [1, 2, 3]},
        ...     "maxItems" : 2,
        ... }
        >>> v = CfnTemplateValidator(schema)
        >>> for error in sorted(v.iter_errors([2, 3, 4]), key=str):
        ...     print(error.message)
        4 is not one of [1, 2, 3]
        [2, 3, 4] is too long

        .. deprecated:: v4.0.0

            Calling this function with a second schema argument is deprecated.
            Use `Validator.evolve` instead.
        """

    def validate(self, instance: Any) -> None:
        """
        Check if the instance is valid under the current `schema`.

        Raises:

            `jsonschema.exceptions.ValidationError`:

                if the instance is invalid

        >>> schema = {"maxItems" : 2}
        >>> CfnTemplateValidator(schema).validate([2, 3, 4])
        Traceback (most recent call last):
            ...
        ValidationError: [2, 3, 4] is too long
        """

    def resolve_value(self, instance: Any) -> ResolutionResult:
        """
        Resolve the given instance, yielding each of its values.

        """

    def evolve(self, **kwargs) -> Validator:
        """
        Create a new validator like this one, but with given changes.

        Preserves all other attributes, so can be used to e.g. create a
        validator with a different schema but with the same :kw:`$ref`
        resolution behavior.

        >>> validator = CfnTemplateValidator({})
        >>> validator.evolve(schema={"type": "number"})
        CfnTemplateValidator(schema={'type': 'number'}, format_checker=None)

        The returned object satisfies the validator protocol, but may not
        be of the same concrete class! In particular this occurs
        when a :kw:`$ref` occurs to a schema with a different
        :kw:`$schema` than this one (i.e. for a different draft).

        >>> validator.evolve(
        ...     schema={"$schema": Draft7Validator.META_SCHEMA["$id"]}
        ... )
        Draft7Validator(schema=..., format_checker=None)
        """

    def extend(
        self,
        validators: dict[str, V] | None,
        function_filter: FunctionFilter | None = None,
        context: Context | None = None,
    ) -> Type[Validator]:
        """
        Extends the validator with a new set of validators to replace VALIDATORS.

        This function recall create with the a merged list of validators from the
        current instance merged with the parameters.

        >>> validator = CfnTemplateValidator({})
        >>> validator.extend(validators={"type": type})
        CfnTemplateValidator(schema={'type': 'number'}, format_checker=None)
        """
