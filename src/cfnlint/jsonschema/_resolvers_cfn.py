"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any, Iterator

import regex as re

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import ResolutionResult
from cfnlint.jsonschema._utils import equal


def unresolvable(validator: Validator, instance: Any) -> ResolutionResult:
    return
    yield


def ref(validator: Validator, instance: Any) -> ResolutionResult:
    if not isinstance(instance, (str, dict)):
        return

    for instance, _, _ in validator.resolve_value(instance):
        if validator.is_type(instance, "string"):
            # if the ref is to pseudo-parameter or parameter we can validate the values
            for v, c in validator.context.ref_value(instance):
                yield v, validator.evolve(context=c), None
            return


def find_in_map(validator: Validator, instance: Any) -> ResolutionResult:
    if not validator.is_type(instance, "array"):
        return
    if len(instance) not in [3, 4]:
        return

    default_value = None
    if len(instance) == 4:
        options = instance[3]
        if validator.is_type(options, "object"):
            if "DefaultValue" in options:
                for value, v, _ in validator.resolve_value(options["DefaultValue"]):
                    yield value, v.evolve(
                        context=v.context.evolve(
                            path=v.context.path.evolve(
                                value_path=deque([4, "DefaultValue"])
                            )
                        ),
                    ), None
                    default_value = value

    for map_name, map_v, _ in validator.resolve_value(instance[0]):
        if not validator.is_type(map_name, "string"):
            continue
        for top_level_key, top_v, _ in validator.resolve_value(instance[1]):
            if validator.is_type(top_level_key, "integer"):
                top_level_key = str(top_level_key)
            if not validator.is_type(top_level_key, "string"):
                continue
            for second_level_key, second_v, err in validator.resolve_value(instance[2]):
                if validator.is_type(second_level_key, "integer"):
                    second_level_key = str(second_level_key)
                if not validator.is_type(second_level_key, "string"):
                    continue
                try:
                    mappings = list(validator.context.mappings.keys())
                    if not default_value and all(
                        not (equal(map_name, each)) for each in mappings
                    ):
                        yield None, map_v.evolve(
                            context=map_v.context.evolve(
                                path=map_v.context.path.evolve(value_path=deque([0])),
                            ),
                        ), ValidationError(
                            f"{map_name!r} is not one of {mappings!r}", path=[0]
                        )
                        continue

                    top_level_keys = list(
                        validator.context.mappings[map_name].keys.keys()
                    )
                    if not default_value and all(
                        not (equal(top_level_key, each)) for each in top_level_keys
                    ):
                        yield None, top_v.evolve(
                            context=top_v.context.evolve(
                                path=top_v.context.path.evolve(value_path=deque([1])),
                            ),
                        ), ValidationError(
                            f"{top_level_key!r} is not one of {top_level_keys!r}",
                            path=[1],
                        )
                        continue

                    second_level_keys = list(
                        validator.context.mappings[map_name]
                        .keys[top_level_key]
                        .keys.keys()
                    )
                    if not default_value and all(
                        not (equal(second_level_key, each))
                        for each in second_level_keys
                    ):
                        yield None, second_v.evolve(
                            context=second_v.context.evolve(
                                path=second_v.context.path.evolve(
                                    value_path=deque([2])
                                ),
                            ),
                        ), ValidationError(
                            f"{second_level_key!r} is not one of {second_level_keys!r}",
                            path=[2],
                        )
                        continue

                    for value in validator.context.mappings[map_name].find_in_map(
                        top_level_key,
                        second_level_key,
                    ):
                        yield (
                            value,
                            validator.evolve(
                                context=validator.context.evolve(
                                    path=validator.context.path.evolve(
                                        value_path=deque(
                                            [
                                                "Mappings",
                                                map_name,
                                                top_level_key,
                                                second_level_key,
                                            ]
                                        )
                                    )
                                )
                            ),
                            None,
                        )
                except KeyError:
                    pass


def get_azs(validator: Validator, instance: Any) -> ResolutionResult:
    if not isinstance(instance, (str, dict)):
        return

    for instance, v, _ in validator.resolve_value(instance):
        if v.is_type(instance, "string"):
            if instance == "":
                for region in v.context.regions:
                    yield (
                        AVAILABILITY_ZONES.get(region),
                        v,
                        None,
                    )
            # if the ref is to pseudo-parameter or parameter we can validate the values
            elif instance in AVAILABILITY_ZONES:
                yield AVAILABILITY_ZONES.get(instance), v, None


def _join_expansion(validator: Validator, instances: Any) -> Iterator[Any]:
    if len(instances) == 0:
        return

    if len(instances) == 1:
        for value, _, _ in validator.resolve_value(instances[0]):
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError(f"Incorrect value type for {value!r}")
            yield [value]
        return

    for value, _, _ in validator.resolve_value(instances[0]):
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError(f"Incorrect value type for {value!r}")
        for values in _join_expansion(validator, instances[1:]):
            yield [value] + values


def join(validator: Validator, instance: Any) -> ResolutionResult:
    # quick validations
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    for delimiter, delimiter_v, _ in validator.resolve_value(instance[0]):
        if not delimiter_v.is_type(delimiter, "string"):
            continue
        for values, values_v, _ in validator.resolve_value(instance[1]):
            if not values_v.is_type(values, "array"):
                continue
            try:
                for value in _join_expansion(values_v, values):
                    yield delimiter.join(value), values_v, None
            except ValueError:
                return


def select(validator: Validator, instance: Any) -> ResolutionResult:
    # quick validations
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    # get the values from the list
    indexes = validator.resolve_value(instance[0])
    objs = validator.resolve_value(instance[1])

    for i, _, _ in indexes:
        for obj, obj_v, _ in objs:
            try:
                i = int(i)
            except ValueError:
                continue
            if not validator.is_type(obj, "array"):
                continue
            if len(obj) <= i:
                continue
            yield from obj_v.resolve_value(obj[i])


def split(validator: Validator, instance: Any) -> ResolutionResult:
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    for delimiter, _, _ in validator.resolve_value(instance[0]):
        for source_string, source_v, _ in validator.resolve_value(instance[1]):
            if not source_v.is_type(delimiter, "string"):
                continue
            if not source_v.is_type(source_string, "string"):
                continue

            yield source_string.split(delimiter), source_v, None


def _sub_parameter_expansion(
    validator: Validator, parameters: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    parameters = parameters.copy()
    if len(parameters) == 0:
        yield {}
        return

    if len(parameters) == 1:
        for key, value in parameters.items():
            for resolved_value, _, _ in validator.resolve_value(value):
                yield {key: resolved_value}
        return

    key = list(parameters.keys())[0]
    value = parameters.pop(key)
    for resolved_value, _, _ in validator.resolve_value(value):
        for values in _sub_parameter_expansion(validator, parameters):
            yield dict({key: resolved_value}, **values)


def _sub_string(validator: Validator, string: str) -> ResolutionResult:
    sub_regex = re.compile(r"(\${([^!].*?)})")

    def _replace(matchobj):
        nonlocal validator
        for value, c in validator.context.ref_value(matchobj.group(2).strip()):
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError(f"Parameter {matchobj.group(2)!r} has wrong type")

            validator = validator.evolve(
                context=validator.context.evolve(
                    ref_values=c.ref_values,
                )
            )
            return value
        raise ValueError(f"No matches for {matchobj.group(2)!r}")

    try:
        yield re.sub(sub_regex, _replace, string), validator, None
    except ValueError:
        return


def sub(validator: Validator, instance: Any) -> ResolutionResult:
    if not (
        validator.is_type(instance, "array") or validator.is_type(instance, "string")
    ):
        return

    if validator.is_type(instance, "array"):
        if len(instance) != 2:
            return

        string = instance[0]
        parameters = instance[1]
        if not validator.is_type(string, "string"):
            return
        if not validator.is_type(parameters, "object"):
            return

        for resolved_parameters in _sub_parameter_expansion(validator, parameters):
            resolved_validator = validator.evolve(
                context=validator.context.evolve(
                    ref_values=resolved_parameters,
                )
            )
            yield from _sub_string(resolved_validator, string)

        return

    # its a string
    yield from _sub_string(validator, instance)


def if_(validator: Validator, instance: Any) -> ResolutionResult:
    if not validator.is_type(instance, "array"):
        return

    if len(instance) != 3:
        return

    for i in [1, 2]:
        for value, v, err in validator.resolve_value(instance[i]):
            yield (
                value,
                v.evolve(
                    context=v.context.evolve(
                        path=v.context.path.evolve(value_path=deque([i])),
                    ),
                ),
                err,
            )


def to_json_string(validator: Validator, instance: Any) -> ResolutionResult:
    for value, v, err in validator.resolve_value(instance):
        yield json.dumps(value), v, err


# not all functions need to be resolved.  These functions
# allow us to pull up values from nested functions
# allowing us to test the possible values against the schema
fn_resolvers: dict[str, Any] = {
    "Fn::Base64": unresolvable,
    "Fn::Cidr": unresolvable,
    "Fn::FindInMap": find_in_map,
    "Fn::ForEach": unresolvable,
    "Fn::GetAtt": unresolvable,
    "Fn::GetAZs": get_azs,
    "Fn::ImportValue": unresolvable,
    "Fn::If": if_,
    "Fn::Join": join,
    "Fn::Select": select,
    "Fn::Split": split,
    "Fn::Sub": sub,
    "Fn::Transform": unresolvable,
    "Fn::ToJsonString": to_json_string,
    "Fn::Equals": unresolvable,
    "Fn::Or": unresolvable,
    "Fn::And": unresolvable,
    "Fn::Not": unresolvable,
    "Condition": unresolvable,
    "Fn::Length": unresolvable,
    "Ref": ref,
}
