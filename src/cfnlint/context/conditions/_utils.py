"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cfnlint.decode.node import Mark, dict_node, list_node
from cfnlint.helpers import is_function

if TYPE_CHECKING:
    from cfnlint.context.context import Context


def get_conditions_from_property(instance: Any, is_root: bool = True) -> set[str]:
    """
    Gets the name of the conditions used directly inside the object.

    We do not look at nested objects for conditions.

    Args:
        instance (Any): The object or listto process.
        is_root (bool): If we are at the root of the object. Default: True.

    Returns:
        set[str]: The set of conditions used in the object or list.
    """
    results: set[str] = set()
    if isinstance(instance, list):
        for v in instance:
            results = results.union(get_conditions_from_property(v, is_root=False))
        return results

    fn_k, fn_v = is_function(instance)
    if fn_k == "Fn::If":
        if isinstance(fn_v, list) and len(fn_v) == 3:
            if isinstance(fn_v[0], str):
                results.add(fn_v[0])
                results = results.union(
                    get_conditions_from_property(fn_v[1], is_root=is_root)
                )
                results = results.union(
                    get_conditions_from_property(fn_v[2], is_root=is_root)
                )
        return results
    if is_root:
        if isinstance(instance, dict):
            for k, v in instance.items():
                results = results.union(get_conditions_from_property(v, is_root=False))
    return results


def build_instance_from_scenario(
    instance: Any,
    scenario: dict[str, bool],
    is_root: bool,
    context: "Context",
) -> Any:
    """
    Get object values from a provided scenario.

    This function recursively processes the provided object, resolving any
    conditional logic (such as Fn::If) based on the given scenario.

    Args:
        instance (Any): The object or listto process.
        scenario (dict): The scenario to use when resolving conditional logic.
        is_root (bool): If we are at the root of the object. Default: True.

    Returns:
        dict or list or any: The processed object, with conditional logic resolved.
        The return type can be a dictionary, list, or any other data type,
        depending on the structure of the input object.
    """

    if isinstance(instance, list):
        new_list: list[Any] = list_node(
            [],
            getattr(instance, "start_mark", Mark(0, 0)),
            getattr(instance, "end_mark", Mark(0, 0)),
        )
        for v in instance:
            new_value = build_instance_from_scenario(
                v,
                scenario,
                is_root=False,
                context=context,
            )
            if new_value is not None:
                new_list.append(new_value)
        return new_list

    if isinstance(instance, dict):
        fn_k, fn_v = is_function(instance)
        if fn_k == "Fn::If" and "Fn::If" in context.functions:
            if isinstance(fn_v, list) and len(fn_v) == 3:
                if isinstance(fn_v[0], str):
                    if_path = scenario.get(fn_v[0], None)
                    if if_path is not None:
                        new_value = build_instance_from_scenario(
                            fn_v[1] if if_path else fn_v[2],
                            scenario,
                            is_root,
                            context=context,
                        )
                        if new_value is not None:
                            return new_value
                        return None
            return instance
        if fn_k == "Ref" and fn_v == "AWS::NoValue" and "Ref" in context.functions:
            return None
        if is_root:
            new_obj: dict[str, Any] = dict_node(
                {},
                getattr(instance, "start_mark", Mark(0, 0)),
                getattr(instance, "end_mark", Mark(0, 0)),
            )
            for k, v in instance.items():
                new_value = build_instance_from_scenario(
                    v,
                    scenario,
                    is_root=False,
                    context=context,
                )
                if new_value is not None:
                    new_obj[k] = new_value
            return new_obj

    return instance
