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

import datetime
import numbers
from dataclasses import dataclass, field
from typing import Any, Callable

from cfnlint.jsonschema.exceptions import UndefinedTypeCheck


def is_array(checker: "TypeChecker", instance: Any) -> bool:
    return isinstance(instance, list)


def is_bool(checker: "TypeChecker", instance: Any) -> bool:
    return isinstance(instance, bool)


def is_integer(checker: "TypeChecker", instance: Any) -> bool:
    # bool inherits from int, so ensure bools aren't reported as ints
    if isinstance(instance, bool):
        return False
    return isinstance(instance, int)


def is_null(checker: "TypeChecker", instance: Any) -> bool:
    return instance is None


def is_number(checker: "TypeChecker", instance: Any) -> bool:
    # bool inherits from int, so ensure bools aren't reported as ints
    if isinstance(instance, bool):
        return False
    return isinstance(instance, numbers.Number)


def is_object(checker: "TypeChecker", instance: Any) -> bool:
    return isinstance(instance, dict)


def is_string(checker: "TypeChecker", instance: Any) -> bool:
    return isinstance(instance, str)


def is_date(checker: "TypeChecker", instance: Any) -> bool:
    return isinstance(instance, datetime.date)


@dataclass(frozen=True, repr=False)
class TypeChecker:
    """
    A :kw:`type` property checker.

    A `TypeChecker` performs type checking for a `Validator`, converting
    between the defined JSON Schema types and some associated Python types or
    objects.

    Modifying the behavior just mentioned by redefining which Python objects
    are considered to be of which JSON Schema types can be done using
    `TypeChecker.redefine` or `TypeChecker.redefine_many`, and types can be
    removed via `TypeChecker.remove`. Each of these return a new `TypeChecker`.

    Arguments:

        type_checkers:

            The initial mapping of types to their checking functions.
    """

    type_checkers: dict[str, Callable[[TypeChecker, Any], bool]] = field(
        init=True, default_factory=dict
    )

    def __repr__(self):
        types = ", ".join(repr(k) for k in sorted(self.type_checkers))
        return f"<{self.__class__.__name__} types={{{types}}}>"

    def is_type(self, instance, type: str) -> bool:
        """
        Check if the instance is of the appropriate type.

        Arguments:

            instance:

                The instance to check

            type:

                The name of the type that is expected.

        Raises:

            `cfnlint.jsonschema.exceptions.UndefinedTypeCheck`:

                if ``type`` is unknown to this object.
        """
        try:
            fn = self.type_checkers[type]
        except KeyError:
            raise UndefinedTypeCheck(type) from None

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
        "date": is_date,
    },
)
