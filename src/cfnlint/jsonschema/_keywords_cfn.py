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
from typing import Any

import regex as re

import cfnlint.jsonschema._keywords as validators_standard
from cfnlint.helpers import (
    BOOLEAN_STRINGS,
    FUNCTION_FOR_EACH,
    FUNCTION_TRANSFORM,
    ensure_list,
    is_function,
)
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import V, ValidationResult
from cfnlint.rules.helpers.get_value_from_path import get_value_from_path

_ap_exception_fns = set([FUNCTION_TRANSFORM, FUNCTION_FOR_EACH])

_UNRESOLVED = object()


def resolve_data_reference(value: Any, root_instance: Any) -> Any:
    """
    Resolve $data and $lookup references in schema values.

    $data uses absolute JSON Pointers to reference values in the instance.
    Example: {"const": {"$data": "/source/fifo"}}

    $lookup resolves a key via $data then maps it through a lookup table.
    Example: {"const": {"$lookup": {"key": {"$data": "/target/type"},
    "map": {"AWS::S3::Bucket": "s3.amazonaws.com"}}}}
    """
    if not isinstance(value, dict):
        return value

    if "$lookup" in value:
        lookup = value["$lookup"]
        if not isinstance(lookup, dict):
            return value
        key = resolve_data_reference(lookup.get("key"), root_instance)
        lookup_map = lookup.get("map", {})
        if isinstance(key, str) and key in lookup_map:
            return lookup_map[key]
        return _UNRESOLVED

    if "$data" not in value:
        return value

    pointer = value["$data"]
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return value

    # Navigate the JSON pointer
    parts = pointer.strip("/").split("/")
    current = root_instance

    try:
        for part in parts:
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
            else:
                return value  # Can't navigate further
        return current
    except (KeyError, IndexError, ValueError):
        return value  # Reference not found, return original


def resolve_data_in_schema(schema: Any, root_instance: Any) -> Any:
    """
    Recursively resolve all $data references in a schema.
    """
    _numeric_keywords = {
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
    }
    _integer_keywords = {
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
    }
    _data_keywords = (
        _numeric_keywords
        | _integer_keywords
        | {
            "const",
            "enum",
            "pattern",
        }
    )
    if isinstance(schema, dict):
        result = {}
        for k, v in schema.items():
            if k in _data_keywords:
                resolved = resolve_data_reference(v, root_instance)
                if resolved is _UNRESOLVED:
                    continue
                if k in _numeric_keywords:
                    try:
                        f = float(resolved)
                        resolved = int(f) if f == int(f) else f
                    except (ValueError, TypeError):
                        continue
                elif k in _integer_keywords:
                    try:
                        resolved = int(resolved)
                    except (ValueError, TypeError):
                        continue
                if k == "pattern" and not isinstance(resolved, str):
                    continue
                result[k] = resolved
            else:
                result[k] = resolve_data_in_schema(v, root_instance)
        return result
    elif isinstance(schema, list):
        return [resolve_data_in_schema(item, root_instance) for item in schema]
    else:
        return schema


def additionalProperties(
    validator: Validator, aP: Any, instance: Any, schema: Any
) -> ValidationResult:
    # is function will just return if one item is present
    # as this is the standard. We will handle exceptions below
    k, _ = is_function(instance)
    if k in validator.context.functions:
        return
    for err in validators_standard.additionalProperties(
        validator, aP, instance, schema
    ):
        # Some functions can exist at the same level
        # so we need to validate that if those functions are
        # currently supported by the context and are part of the
        # error

        # if the path is 0 just yield the error and return
        # this should never happen
        if not len(err.path) > 0:  # pragma: no cover
            yield err  # pragma: no cover
            return  # pragma: no cover

        for fn in list(_ap_exception_fns & set(validator.context.functions)):
            if re.fullmatch(fn, str(err.path[0])):  # type: ignore
                break
        else:
            yield err


def cfnContext(
    validator: Validator,
    s: Any,
    instance: Any,
    schema: Any,
) -> ValidationResult:
    context_parameters: dict[str, Any] = {}

    functions = s.get("functions")
    if functions is not None:
        if validator.is_type(functions, "object"):
            if "$ref" in functions:
                _, functions = validator.resolver.resolve(functions["$ref"])
            else:
                functions = []

    pseudo_parameters = s.get("pseudoParameters")
    if pseudo_parameters is not None:
        context_parameters["pseudo_parameters"] = set(pseudo_parameters)

    references = s.get("references")
    if references is not None:
        if "Resources" not in references:
            context_parameters["resources"] = {}

    if functions is not None:
        context_parameters["functions"] = functions

    cfn_validator = validator.evolve(
        context=validator.context.evolve(**context_parameters)
    )

    yield from cfn_validator.descend(
        instance=instance,
        schema=s.get("schema", {}),
        schema_path="schema",
    )


def dynamicValidation(
    validator: Validator, dV: Any, instance: Any, schema: dict[str, Any]
) -> ValidationResult:
    """
    Performs dynamic validation based on context.

    The dynamicValidation keyword supports:
    - context: The context source to validate against
               (parameters, conditions, resources, etc.)
    - transformCheck: Check if a specific transform exists
                      (returns true/false for if/then/else)
    - pathCheck: Validate based on the current path in the template
    """
    if not validator.is_type(dV, "object"):
        return

    # Handle transform check (for use with if/then/else)
    transform_check = dV.get("transformCheck")
    if transform_check is not None:
        if transform_check not in validator.context.transforms.transforms:
            yield ValidationError(
                f"Transform {transform_check!r} is required "
                "but not present in the template"
            )

    # Handle dynamic source validation
    context_source = dV.get("context")
    if context_source is not None:
        if context_source and isinstance(context_source, str):
            # Get the appropriate collection based on the context source
            collection = None
            if context_source == "conditions":
                collection = list(validator.context.conditions.conditions.keys())
            elif context_source == "mappings":
                collection = list(validator.context.mappings.maps.keys())
            elif context_source == "refs":
                collection = validator.context.refs

            if collection is not None:
                # Build a dynamic schema with an enum of valid values
                dynamic_schema: dict[str, Any] = {"enum": collection}

                # For refs, also allow module sub-resource names
                if context_source == "refs":
                    module_names = validator.context.module_names
                    if module_names:
                        patterns = [{"pattern": f"^{name}.+"} for name in module_names]
                        dynamic_schema = {"anyOf": [dynamic_schema] + patterns}

                # Use descend to validate against the dynamic schema
                yield from validator.descend(
                    instance=instance,
                    schema=dynamic_schema,
                )

    path_check = dV.get("pathCheck")
    if path_check:
        current_path = "/".join(str(p) for p in validator.context.path.path)
        pattern_schema = {"pattern": f"^{path_check}.*$"}

        yield from validator.descend(
            instance=current_path,
            schema=pattern_schema,
        )


#####
# Type checks
#####
def _raw_type(validator: Validator, tS: Any, instance: Any) -> bool:
    if tS in ["object", "array", "null"] or validator.is_type(instance, "null"):
        return validator.is_type(instance, tS)
    if "string" == tS:
        if validator.is_type(instance, "object") or validator.is_type(
            instance, "array"
        ):
            return False
        return True
    if "number" == tS:
        if validator.is_type(instance, "boolean"):
            return False
        try:
            float(instance)
            return True
        except (ValueError, TypeError):
            return False
    if "integer" == tS:
        if validator.is_type(instance, "boolean"):
            return False
        try:
            int(instance)
            return True
        except (ValueError, TypeError):
            return False
    if "boolean" == tS:
        if validator.is_type(instance, "boolean"):
            return True
        if instance in list(BOOLEAN_STRINGS):
            return True
    return False


def _raw_type_strict(validator: Validator, tS: Any, instance: Any) -> bool:
    return validator.is_type(instance, tS)


# pylint: disable=unused-argument
def cfn_type(validator: Validator, tS: Any, instance: Any, schema: Any):
    """
    When evaluating a type in CloudFormation we have to account
    for the intrinsic functions that the values can represent
    (Ref, GetAtt, If, ...).  This will evaluate if the correct type
    is not found and the instance is an object with a function
    that we do our best to evaluate if that function represents the
    type we are looking for
    """
    if validator.context.strict_types:
        raw_type_fn = _raw_type_strict
    else:
        raw_type_fn = _raw_type
    tS = ensure_list(tS)
    if not any(raw_type_fn(validator, type, instance) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


def cfnGather(
    validator: Validator, s: dict[str, Any], instance: Any, schema: dict[str, Any]
) -> ValidationResult:
    """
    Gather properties from local and remote resources, validate with schema.

    Each "gather" entry is local (no "reference") or remote (has "reference").
    The first remote entry drives iteration — its reference is followed to find
    the target resource. All entries' properties are gathered into a flat dict
    keyed by entry name, then validated against "schema" with $data support.
    """
    gather_spec = s.get("gather", {})
    validation_schema = s.get("schema", {})

    # Split entries into local and remote
    local_entries: dict[str, dict[str, Any]] = {}
    remote_entries: dict[str, dict[str, Any]] = {}
    for name, spec in gather_spec.items():
        if "reference" in spec:
            remote_entries[name] = spec
        else:
            local_entries[name] = spec

    if not remote_entries:
        if local_entries:
            gathered, path_maps = _gather_locals(validator, instance, local_entries)
            yield from _validate_gathered(
                validator,
                gathered,
                path_maps,
                {},
                local_entries,
                validation_schema,
            )
        return

    primary_name = next(iter(remote_entries))
    primary_spec = remote_entries[primary_name]
    ref_path = _to_path(primary_spec["reference"])

    for ref_value, scenario_validator in get_value_from_path(
        validator, instance, ref_path
    ):
        if ref_value is None:
            continue

        resource_name = _resolve_reference(ref_value)

        # Unrecognized function — skip
        if resource_name is None:
            if isinstance(ref_value, dict):
                continue
            # Plain value — validate local entries only
            gathered, path_maps = _gather_locals(
                scenario_validator, instance, local_entries
            )
            yield from _validate_gathered(
                scenario_validator,
                gathered,
                path_maps,
                {},
                local_entries,
                validation_schema,
            )
            continue

        if resource_name not in validator.context.resources:
            continue

        target_type = validator.context.resources.get(resource_name, None)

        if not _matches_filter(target_type.type if target_type else None, primary_spec):
            continue

        # Gather all entries
        gathered, path_maps = _gather_locals(
            scenario_validator, instance, local_entries
        )
        resource_names: dict[str, str] = {}

        # Gather all remote entries
        for name, spec in remote_entries.items():
            if name == primary_name:
                rn: str | None = resource_name
                rtype: str | None = target_type.type if target_type else None
            else:
                rn, rtype = _resolve_remote(
                    validator, scenario_validator, instance, spec
                )
            if rn is None:
                continue

            props_spec = spec.get("properties", {})
            gathered[name] = _gather_properties(
                scenario_validator, rn, instance, props_spec, rtype
            )
            path_maps[name] = {k: _prop_path(v) for k, v in props_spec.items()}
            resource_names[name] = rn

        yield from _validate_gathered(
            scenario_validator,
            gathered,
            path_maps,
            resource_names,
            local_entries,
            validation_schema,
        )


def _to_path(path_str: str) -> deque[str | int]:
    if not path_str or path_str == ".":
        return deque()
    return deque(path_str.strip("/").split("/"))


def _prop_path(spec: str | dict[str, Any]) -> list[str]:
    path: str = spec if isinstance(spec, str) else spec.get("path", "")
    return path.strip("/").split("/")


def _resolve_reference(ref_value: Any) -> str | None:
    fn_k, fn_v = is_function(ref_value)
    if fn_k == "Ref" and isinstance(fn_v, str):
        return fn_v
    if fn_k == "Fn::GetAtt":
        if isinstance(fn_v, list) and fn_v:
            return str(fn_v[0])
        if isinstance(fn_v, str):
            return fn_v.split(".")[0]
    return None


def _matches_filter(resource_type: str | None, spec: dict[str, Any]) -> bool:
    target_filter = spec.get("filter", {})
    if target_filter and "type" in target_filter:
        return bool(resource_type == target_filter["type"])
    return True


def _resolve_remote(
    validator: Validator,
    scenario_validator: Validator,
    instance: Any,
    spec: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Follow a remote entry's reference and return (resource_name, type)."""
    ref_path = _to_path(spec["reference"])
    for rv, _ in get_value_from_path(scenario_validator, instance, ref_path):
        if rv is None:
            continue
        rn = _resolve_reference(rv)
        if not rn or rn not in validator.context.resources:
            continue
        rtype = validator.context.resources[rn].type
        if not _matches_filter(rtype, spec):
            continue
        return rn, rtype
    return None, None


def _gather_properties(
    validator: Validator,
    resource_name: str | None,
    instance: Any,
    specs: dict[str, Any],
    resource_type: str | None = None,
) -> dict[str, Any]:
    """Gather property values using get_value_from_path for condition resolution."""
    gathered: dict[str, Any] = {}
    template = validator.cfn.template

    for key, spec in specs.items():
        if isinstance(spec, str) and spec == "$type":
            if resource_type:
                gathered[key] = resource_type
            continue

        if isinstance(spec, str):
            path, default, has_default = spec, None, False
        else:
            path = spec.get("path", "")
            default = spec.get("default")
            has_default = "default" in spec

        path_parts = _to_path(path)

        # Build full path through template for remote, or use instance for local
        if resource_name is not None:
            source = template
            full_path = deque[str | int](["Resources", resource_name, "Properties"])
            full_path.extend(path_parts)
        else:
            source = instance
            full_path = path_parts

        value = None
        found = False
        for val, _ in get_value_from_path(validator, source, full_path.copy()):
            if val is None:
                continue
            fn_k, fn_v = is_function(val)
            if fn_k == "Ref" and fn_v == "AWS::NoValue":
                continue
            value = val
            found = True
            break

        if not found:
            if has_default:
                gathered[key] = default
            continue

        gathered[key] = value
    return gathered


def _gather_locals(
    scenario_validator: Validator,
    instance: Any,
    local_entries: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, dict[str, list[str]]]]:
    """Gather properties for all local entries."""
    gathered: dict[str, Any] = {}
    path_maps: dict[str, dict[str, list[str]]] = {}
    for name, spec in local_entries.items():
        props_spec = spec.get("properties", {})
        gathered[name] = _gather_properties(
            scenario_validator, None, instance, props_spec
        )
        path_maps[name] = {k: _prop_path(v) for k, v in props_spec.items()}
    return gathered, path_maps


def _validate_gathered(
    scenario_validator: Validator,
    gathered: dict[str, Any],
    path_maps: dict[str, dict[str, list[str]]],
    resource_names: dict[str, str],
    local_entries: dict[str, dict[str, Any]],
    validation_schema: dict[str, Any],
) -> ValidationResult:
    """Validate gathered object and remap error paths."""
    resolved_schema = resolve_data_in_schema(validation_schema, gathered)
    for err in scenario_validator.descend(
        gathered, resolved_schema, schema_path="schema"
    ):
        if not err.path:
            yield err
            continue

        err_path = list(err.path)
        entry_name = err_path[0]
        real_path = _remap_path(err_path, path_maps)

        if entry_name in resource_names:
            err.path_override = (
                deque[str | int](
                    ["Resources", resource_names[entry_name], "Properties"]
                )
                + real_path
            )
            err.path = deque()
        elif entry_name in local_entries:
            err.path = real_path
        yield err


def _remap_path(
    err_path: list[str | int],
    path_maps: dict[str, dict[str, list[str]]],
) -> deque[str | int]:
    """Remap a gathered-object error path back to the original property path."""
    entry_name = str(err_path[0])
    if (
        len(err_path) > 1
        and entry_name in path_maps
        and str(err_path[1]) in path_maps[entry_name]
    ):
        real = deque[str | int](path_maps[entry_name][str(err_path[1])])
        real.extend(err_path[2:])
        return real
    return deque(err_path[1:])


def _function_unknown(
    validator: Validator, s: Any, instance: Any, schema: dict[str, Any]
) -> ValidationResult:
    """Default validator for CloudFormation intrinsic functions.
    Returns unknown error in unresolvable mode to prevent incorrect validation.
    Overridden by function rules in full validation environments."""
    if validator.context.unresolvable_function_mode:
        yield ValidationError(
            "Cannot resolve function in composite validation",
            unknown=True,
        )
    # In normal mode, do nothing - let the function pass through
    return


cfn_validators: dict[str, V] = {
    "additionalProperties": additionalProperties,
    "cfnContext": cfnContext,
    "cfnGather": cfnGather,
    "dynamicValidation": dynamicValidation,
    "type": cfn_type,
    # CloudFormation intrinsic functions - default to unknown
    "ref": _function_unknown,
    "fn_base64": _function_unknown,
    "fn_cidr": _function_unknown,
    "fn_findinmap": _function_unknown,
    "fn_getatt": _function_unknown,
    "fn_getazs": _function_unknown,
    "fn_importvalue": _function_unknown,
    "fn_join": _function_unknown,
    "fn_select": _function_unknown,
    "fn_split": _function_unknown,
    "fn_sub": _function_unknown,
    "fn_transform": _function_unknown,
    "fn_tojsonstring": _function_unknown,
    "fn_length": _function_unknown,
    "fn_if": _function_unknown,
    "fn_getstackoutput": _function_unknown,
}
