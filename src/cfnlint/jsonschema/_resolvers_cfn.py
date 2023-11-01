import json
from typing import Any, Dict, Iterator

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.jsonschema import Validator


def unresolvable(validator: Validator, instance: Any) -> Iterator[Any]:
    return
    yield


def ref(validator: Validator, instance: Any) -> Iterator[Any]:
    if not isinstance(instance, (str, dict)):
        return

    for instance in validator.resolve_value(instance):
        if validator.is_type(instance, "string"):
            # if the ref is to pseudo-parameter or parameter we can validate the values
            if instance in validator.context.ref_values:
                # Ref: AWS::NoValue returns None making this fail
                if validator.context.ref_values[instance] is not None:
                    yield from iter(validator.context.ref_values[instance])
                    return
            if instance in validator.context.parameters:
                if validator.context.parameters[instance].allowed_values:
                    yield from iter(
                        validator.context.parameters[instance].allowed_values
                    )
                if validator.context.parameters[instance].default is not None:
                    yield validator.context.parameters[instance].default
                return
            return


def find_in_map(validator: Validator, instance: Any) -> Iterator[Any]:
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 3:
        return

    # get the values from the list
    map_names = validator.resolve_value(instance[0])
    top_level_keys = validator.resolve_value(instance[1])
    second_level_keys = validator.resolve_value(instance[2])

    for map_name in map_names:
        if not validator.is_type(map_name, "string"):
            continue
        for top_level_key in top_level_keys:
            if not validator.is_type(top_level_key, "string"):
                continue
            for second_level_key in second_level_keys:
                if not validator.is_type(second_level_key, "string"):
                    continue
                if map_name in validator.context.mappings:
                    try:
                        yield validator.context.mappings[map_name].find_in_map(
                            top_level_key,
                            second_level_key,
                        )
                    except KeyError:
                        pass


def get_azs(validator: Validator, instance: Any) -> Iterator[Any]:
    if not isinstance(instance, (str, dict)):
        return

    for instance in validator.resolve_value(instance):
        if validator.is_type(instance, "string"):
            if instance == "":
                instance = validator.context.region
            # if the ref is to pseudo-parameter or parameter we can validate the values
            if instance in AVAILABILITY_ZONES:
                yield AVAILABILITY_ZONES.get(instance)


def _join_expansion(validator: Validator, instances: Any) -> Iterator[Any]:
    if len(instances) == 0:
        return

    if len(instances) == 1:
        for value in validator.resolve_value(instances[0]):
            yield [value]
        return

    for value in validator.resolve_value(instances[0]):
        for values in _join_expansion(validator, instances[1:]):
            yield [value] + values


def join(validator: Validator, instance: Any) -> Iterator[Any]:
    # quick validations
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    for delimiter in validator.resolve_value(instance[0]):
        if not validator.is_type(delimiter, "string"):
            continue
        for values in validator.resolve_value(instance[1]):
            if not validator.is_type(values, "array"):
                continue
            for value in _join_expansion(validator, values):
                yield delimiter.join(value)


def select(validator: Validator, instance: Any) -> Iterator[Any]:
    # quick validations
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    # get the values from the list
    indexes = validator.resolve_value(instance[0])
    objs = validator.resolve_value(instance[1])

    for i in indexes:
        for obj in objs:
            try:
                i = int(i)
            except ValueError:
                continue
            if not validator.is_type(obj, "array"):
                continue
            if len(obj) <= i:
                continue
            yield obj[i]


def split(validator: Validator, instance: Any) -> Iterator[Any]:
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    for delimiter in validator.resolve_value(instance[0]):
        for source_string in validator.resolve_value(instance[1]):
            if not validator.is_type(delimiter, "string"):
                continue
            if not validator.is_type(source_string, "string"):
                continue

            yield source_string.split(delimiter)


def sub(validator: Validator, instance: Any) -> Iterator[Any]:
    return
    yield


def to_json_string(validator: Validator, instance: Any) -> Iterator[Any]:
    instance = validator.resolve_value(instance)

    yield json.dumps(instance)


# not all functions need to be resolved.  These functions
# allow us to pull up values from nested functions
# allowing us to test the possible values against the schema
fn_resolvers: Dict[str, Any] = {
    "Fn::Base64": unresolvable,
    "Fn::Cidr": unresolvable,
    "Fn::FindInMap": find_in_map,
    "Fn::GetAtt": unresolvable,
    "Fn::GetAZs": get_azs,
    "Fn::ImportValue": unresolvable,
    "Fn::Join": join,
    "Fn::Select": select,
    "Fn::Split": split,
    "Fn::Sub": sub,
    "Fn::Transform": unresolvable,
    "Fn::ToJsonString": to_json_string,
    "Ref": ref,
}
