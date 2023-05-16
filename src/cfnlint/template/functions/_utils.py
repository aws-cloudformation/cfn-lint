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
        for i, item in enumerate(lists):
            results.append(item[:] + [fn(add_item)])

    return results
