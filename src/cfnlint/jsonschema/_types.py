"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Originally taken from https://raw.githubusercontent.com/python-jsonschema/jsonschema/main/jsonschema/_types.py
adapted for CloudFormation usage
"""

from __future__ import annotations

import numbers
import typing

import attr
from jsonschema.exceptions import UndefinedTypeCheck
from pyrsistent import pmap
from pyrsistent.typing import PMap


# unfortunately, the type of pmap is generic, and if used as the attr.ib
# converter, the generic type is presented to mypy, which then fails to match
# the concrete type of a type checker mapping
# this "do nothing" wrapper presents the correct information to mypy
def _typed_pmap_converter(
    init_val: typing.Mapping[
        str,
        typing.Callable[["TypeChecker", typing.Any], bool],
    ],
) -> PMap[str, typing.Callable[["TypeChecker", typing.Any], bool]]:
    return pmap(init_val)


# pylint: disable=unused-argument
def is_array(checker, instance):
    return isinstance(instance, list)


# pylint: disable=unused-argument
def is_bool(checker, instance):
    return isinstance(instance, bool)


# pylint: disable=unused-argument
def is_integer(checker, instance):
    # bool inherits from int, so ensure bools aren't reported as ints
    if isinstance(instance, bool):
        return False
    return isinstance(instance, int)


# pylint: disable=unused-argument
def is_null(checker, instance):
    return instance is None


# pylint: disable=unused-argument
def is_number(checker, instance):
    # bool inherits from int, so ensure bools aren't reported as ints
    if isinstance(instance, bool):
        return False
    return isinstance(instance, numbers.Number)


# pylint: disable=unused-argument
def is_object(checker, instance):
    return isinstance(instance, dict)


# pylint: disable=unused-argument
def is_string(checker, instance):
    return isinstance(instance, str)


@attr.s(frozen=True, repr=False)
class TypeChecker:
    """
    A :kw:`type` property checker.

    A `TypeChecker` performs type checking for a `Validator`, converting
    between the defined JSON Schema types and some associated Python types or
    objects.

    """

    _type_checkers: PMap[
        str,
        typing.Callable[["TypeChecker", typing.Any], bool],
    ] = attr.ib(
        default=pmap(),
        converter=_typed_pmap_converter,
    )

    def __repr__(self):
        types = ", ".join(repr(k) for k in sorted(self._type_checkers))
        return f"<{self.__class__.__name__} types={{{types}}}>"

    def is_type(self, instance, t: str) -> bool:
        """
        Check if the instance is of the appropriate type.

        Arguments:

            instance:

                The instance to check

            t:

                The name of the type that is expected.

        Raises:

            `jsonschema.exceptions.UndefinedTypeCheck`:

                if ``type`` is unknown to this object.
        """
        try:
            fn = self._type_checkers[t]
        except KeyError:
            raise UndefinedTypeCheck(t) from None

        return fn(self, instance)


cfn_type_checker = TypeChecker(
    {
        "array": is_array,
        "boolean": is_bool,
        "integer": lambda checker, instance: (
            is_integer(checker, instance)
            or isinstance(instance, float)
            and instance.is_integer()
        ),
        "object": is_object,
        "null": is_null,
        "number": is_number,
        "string": is_string,
    },
)
