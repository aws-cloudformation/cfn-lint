import json
from typing import Any, Dict, Iterator

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.jsonschema import Validator


def unresolvable(self, validator: Validator, instance: Any) -> Iterator[Any]:
    return
    yield


def ref(validator: Validator, instance: Any) -> Iterator[Any]:
    if validator.is_type(instance, "object"):
        instances = list(validator.resolve(instance))
    if validator.is_type(instance, "string"):
        instances = [instance]

    for instance in instances:
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
                if validator.context.parameters[instance].default:
                    yield validator.context.parameters[instance].default
                return
            return


def find_in_map(validator: Validator, instance: Any) -> Iterator[Any]:
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 3:
        return

    # get the values from the list
    map_names = validator.resolve(instance[0])
    top_level_keys = validator.resolve(instance[1])
    second_level_keys = validator.resolve(instance[2])

    for map_name in map_names:
        if not validator.is_type(map_name, "string"):
            continue
        for top_level_key in top_level_keys:
            if not validator.is_type(top_level_key, "string"):
                continue
            for second_level_key in second_level_keys:
                if not validator.is_type(second_level_key, "string"):
                    continue
                if map_name in validator.context.maps:
                    if top_level_key in validator.context.maps[map_name]:
                        if (
                            second_level_key
                            in validator.context.maps[map_name][top_level_key]
                        ):
                            yield validator.context.maps[map_name][top_level_key][
                                second_level_key
                            ]


def get_azs(validator: Validator, instance: Any) -> Iterator[Any]:
    instances = None
    if validator.is_type(instance, "object"):
        instances = list(validator.resolve(instance))
    if validator.is_type(instance, "string"):
        instances = [instance]

    if instances is None:
        return

    for instance in instances:
        if validator.is_type(instance, "string"):
            # if the ref is to pseudo-parameter or parameter we can validate the values
            if instance in AVAILABILITY_ZONES:
                yield AVAILABILITY_ZONES.get(instance)


def join(validator: Validator, instance: Any) -> Iterator[Any]:
    # quick validations
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    # get the values from the list
    delimiters = validator.resolve(instance[0])
    values = validator.resolve(instance[1])

    for delimiter in delimiters:
        for value in values:
            if not validator.is_type(delimiter, "string"):
                continue
            if not validator.is_type(value, "array"):
                continue
            yield value.join(delimiter)


def select(validator: Validator, instance: Any) -> Iterator[Any]:
    # quick validations
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return

    # get the values from the list
    indexes = validator.resolve(instance[0])
    objs = validator.resolve(instance[1])

    for i in indexes:
        for obj in objs:
            try:
                i = int(i)
            except ValueError:
                continue
            if validator.is_type(obj, "array"):
                yield obj[i]
            yield obj[i]


def split(validator: Validator, instance: Any) -> Iterator[Any]:
    if not validator.is_type(instance, "array"):
        return
    if not len(instance) == 2:
        return
    delimiters = validator.resolve(instance[0])
    source_strings = validator.resolve(instance[1])

    for delimiter in delimiters:
        for source_string in source_strings:
            if validator.is_type(delimiter, "string"):
                continue
            if validator.is_type(source_string, "string"):
                continue
            yield source_string.split(delimiter)


def sub(validator: Validator, instance: Any) -> Iterator[Any]:
    return
    yield


def to_json_string(validator: Validator, instance: Any) -> Iterator[Any]:
    instance = validator.resolve(instance)

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
