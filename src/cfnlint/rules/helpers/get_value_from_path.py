"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

from cfnlint.context.conditions import Unsatisfiable
from cfnlint.helpers import is_function
from cfnlint.jsonschema import Validator


def _get_relationship_fn_if(
    validator: Validator, key: Any, value: Any, path: deque[str | int]
) -> Iterator[tuple[Any, Validator]]:
    if not isinstance(value, list) or len(value) != 3:
        return
    condition = value[0]

    for i in [1, 2]:
        try:
            if_validator = validator.evolve(
                context=validator.context.evolve(
                    conditions=validator.context.conditions.evolve(
                        status={
                            condition: True if i == 1 else False,
                        },
                    ),
                    path=validator.context.path.descend(path=key).descend(path=i),
                )
            )
            for r, v in get_value_from_path(
                if_validator,
                value[i],
                path.copy(),
            ):
                yield r, v
        except Unsatisfiable:
            pass


def _get_value_from_path_list(
    validator: Validator, instance: Any, path: deque[str | int]
) -> Iterator[tuple[Any, Validator]]:
    for i, v in enumerate(instance):
        for r, v in get_value_from_path(
            validator.evolve(
                context=validator.context.evolve(
                    path=validator.context.path.descend(path=i)
                ),
            ),
            v,
            path.copy(),
        ):
            yield r, v


def get_value_from_path(
    validator: Validator, instance: Any, path: deque[str | int]
) -> Iterator[tuple[Any, Validator]]:
    """
    Retrieve a value from a nested dictionary or list using a path.

    Args:
        validator (Validator): The validator instance
        data (Any): The dictionary or list to search.
        path (deque[str | int]): The path to the value.

    Returns:
        The value at the specified path, or None if the key doesn't exist.

    Examples:
        >>> data = {'a': {'b': {'c': 3}}}
        >>> get_value_from_path(data, ['a', 'b', 'c'])
        3
    """

    fn_k, fn_v = is_function(instance)
    if fn_k is not None:
        if fn_k == "Fn::If":
            yield from _get_relationship_fn_if(validator, fn_k, fn_v, path)
        elif fn_k == "Ref" and fn_v == "AWS::NoValue":
            yield None, validator.evolve(
                context=validator.context.evolve(
                    path=validator.context.path.descend(path=fn_k)
                )
            )
        elif not path:
            yield instance, validator
        return

    if not path:
        yield instance, validator
        return

    key = path.popleft()
    if isinstance(instance, list) and key == "*":
        yield from _get_value_from_path_list(validator, instance, path)
        return

    if not isinstance(instance, dict):
        yield None, validator
        return

    for r, v in get_value_from_path(
        validator.evolve(
            context=validator.context.evolve(
                path=validator.context.path.descend(path=key)
            )
        ),
        instance.get(key),
        path.copy(),
    ):
        yield r, v

    return
