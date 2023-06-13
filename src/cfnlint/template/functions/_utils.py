"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any, Callable, List, Sequence, Tuple

from cfnlint.template.functions.exceptions import Unpredictable


def add_to_lists(
    lists: Sequence[Any],
    add_list: Sequence[Any],
    types: Tuple[Any, ...],
    fn: Callable[[Any], Any],
) -> List[Any]:
    results = []
    for add_item in add_list:
        if not isinstance(add_item, types):
            raise Unpredictable(f"Fn::Join can only join strings {add_item!r}")
        if not lists:
            results.append([fn(add_item)])
            return results
        for item in lists:
            results.append(item[:] + [fn(add_item)])
    return results
