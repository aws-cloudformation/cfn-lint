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

from collections import deque
from copy import deepcopy
from difflib import SequenceMatcher
from typing import Any, Dict, Sequence

import regex as re

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._typing import ValidationResult
from cfnlint.jsonschema._utils import (
    ensure_list,
    equal,
    find_additional_properties,
    unbool,
    uniq,
    uniq_keys,
)
from cfnlint.jsonschema.exceptions import FormatError


def additionalProperties(
    validator: Validator, aP: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return

    extras = set(find_additional_properties(validator, instance, schema))
    if validator.is_type(aP, "object"):
        for extra in extras:
            yield from validator.descend(
                instance[extra],
                aP,
                path=extra,
                property_path="*",
            )
    elif not aP and extras:
        if "patternProperties" in schema:
            patterns = ", ".join(
                repr(each) for each in sorted(schema["patternProperties"])
            )
            for extra in extras:
                error = f"{extra!r} does not match any of the regexes: {patterns}"
                yield ValidationError(error, path=[extra])
        else:
            for extra in extras:
                for key in schema.get("properties", {}).keys():
                    if SequenceMatcher(a=extra, b=key).ratio() > 0.8:
                        yield ValidationError(
                            (
                                f"Additional properties are not allowed ({extra!r} "
                                f"was unexpected. Did you mean {key!r}?)"
                            ),
                            path=[extra],
                        )
                        break
                else:
                    yield ValidationError(
                        (
                            f"Additional properties are not allowed ({extra!r} "
                            "was unexpected)"
                        ),
                        path=[extra],
                    )


def allOf(
    validator: Validator, allOf: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    for index, subschema in enumerate(allOf):
        yield from validator.descend(instance, subschema, schema_path=index)


def anyOf(
    validator: Validator, anyOf: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    all_errors = []
    for index, subschema in enumerate(anyOf):
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            f"{instance!r} is not valid under any of the given schemas",
            context=all_errors,
        )


def const(
    validator: Validator, const: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not equal(instance, const):
        yield ValidationError(f"{const!r} was expected")


def contains(
    validator: Validator, contains: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "array"):
        return

    if not any(
        validator.evolve(schema=contains).is_valid(element) for element in instance
    ):
        yield ValidationError(
            f"{instance!r} does not contain items matching the given schema",
        )


def dependencies(
    validator: Validator, dependencies: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in dependencies.items():
        if property not in instance:
            continue

        if validator.is_type(dependency, "array"):
            for each in dependency:
                if each not in instance:
                    message = f"{each!r} is a dependency of {property!r}"
                    yield ValidationError(message)
        else:
            yield from validator.descend(
                instance,
                dependency,
                schema_path=property,
            )


def dependentRequired(
    validator: Validator,
    dependentRequired: Dict[str, Sequence[str]],
    instance: Any,
    schema: Dict[str, Any],
):
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in dependentRequired.items():
        if property not in instance:
            continue

        for each in dependency:
            if each not in instance:
                message = f"{each!r} is a dependency of {property!r}"
                yield ValidationError(message)


def dependentExcluded(
    validator: Validator,
    dependentExcluded: Dict[str, Sequence[str]],
    instance: Any,
    schema: Dict[str, Any],
):
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in dependentExcluded.items():
        if property not in instance:
            continue

        for each in dependency:
            if each in instance:
                message = f"{each!r} should not be included with {property!r}"
                yield ValidationError(message, path=[each])


def enum(
    validator: Validator, enums: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if instance in (0, 1):
        unbooled = unbool(instance)
        if all(not (equal(unbooled, unbool(each))) for each in enums):
            yield ValidationError(f"{instance!r} is not one of {enums!r}")
    else:
        if all(not (equal(instance, each)) for each in enums):
            yield ValidationError(f"{instance!r} is not one of {enums!r}")


def exclusiveMaximum(
    validator: Validator, m: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    t_instance = deepcopy(instance)
    if validator.is_type(t_instance, "string"):
        try:
            t_instance = float(t_instance)
        except ValueError:
            return
    if not validator.is_type(t_instance, "number"):
        return

    if t_instance >= m:
        yield ValidationError(
            f"{instance!r} is greater than or equal to the maximum of {m!r}",
        )


def exclusiveMinimum(
    validator: Validator, m: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    t_instance = deepcopy(instance)
    if validator.is_type(t_instance, "string"):
        try:
            t_instance = float(t_instance)
        except ValueError:
            return
    if not validator.is_type(t_instance, "number"):
        return

    if t_instance <= m:
        yield ValidationError(
            f"{instance!r} is less than or equal to the minimum of {m!r}",
        )


def format(
    validator: Validator, format: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if validator._format_checker is not None:  # type: ignore
        try:
            validator._format_checker.check(instance, format)  # type: ignore
        except FormatError as error:
            yield ValidationError(error.message, cause=error.cause)


def if_(
    validator: Validator, if_schema: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if validator.evolve(schema=if_schema).is_valid(instance):
        if "then" in schema:
            then = schema["then"]
            yield from validator.descend(instance, then, schema_path="then")
    elif "else" in schema:
        else_ = schema["else"]
        yield from validator.descend(instance, else_, schema_path="else")


def items(
    validator: Validator, items: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "array"):
        return

    if validator.is_type(items, "array"):
        for (index, item), subschema in zip(enumerate(instance), items):
            yield from validator.descend(
                item,
                subschema,
                path=index,
                schema_path=index,
                property_path="*",
            )
    else:
        for index, item in enumerate(instance):
            yield from validator.descend(item, items, path=index, property_path="*")


def maxItems(
    validator: Validator, mI: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:  # pylint: disable=arguments-renamed
    if validator.is_type(instance, "array") and len(instance) > mI:
        yield ValidationError(f"{instance!r} is too long ({mI})")


def maxLength(
    validator: Validator, mL: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:  # pylint: disable=arguments-renamed
    if not validator.is_type(instance, "string"):
        return

    if len(instance) > mL:
        yield ValidationError(f"{instance!r} is longer than {mL}")


def maxProperties(
    validator: Validator, mP: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return
    if validator.is_type(instance, "object") and len(instance) > mP:
        yield ValidationError(f"{instance!r} has too many properties")


def maximum(
    validator: Validator, m: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    t_instance = deepcopy(instance)
    if validator.is_type(t_instance, "string"):
        try:
            t_instance = float(t_instance)
        except:  # noqa: E722
            return
    if not validator.is_type(t_instance, "number"):
        return

    if t_instance > m:
        message = f"{instance!r} is greater than the maximum of {m!r}"
        yield ValidationError(message)


def minItems(
    validator: Validator, mI: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if validator.is_type(instance, "array") and len(instance) < mI:
        yield ValidationError(f"{instance!r} is too short ({mI})")


def minLength(
    validator: Validator, mL: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:  # pylint: disable=arguments-renamed
    if not validator.is_type(instance, "string"):
        return

    if len(instance) < mL:
        yield ValidationError(f"{instance!r} is shorter than {mL}")


def minProperties(
    validator: Validator, mP: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if validator.is_type(instance, "object") and len(instance) < mP:
        yield ValidationError(f"{instance!r} does not have enough properties")


def minimum(
    validator: Validator, m: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    t_instance = deepcopy(instance)
    if validator.is_type(t_instance, "string"):
        try:
            t_instance = float(t_instance)
        except ValueError:
            return
    if not validator.is_type(t_instance, "number"):
        return

    if t_instance < m:
        message = f"{instance!r} is less than the minimum of {m!r}"
        yield ValidationError(message)


def multipleOf(
    validator: Validator, dB: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    t_instance = deepcopy(instance)
    if validator.is_type(t_instance, "string"):
        try:
            t_instance = float(t_instance)
        except ValueError:
            return
    if not validator.is_type(t_instance, "number"):
        return

    if isinstance(dB, float):
        quotient = t_instance / dB
        try:
            failed = int(quotient) != quotient
        except OverflowError:
            pass
    else:
        failed = t_instance % dB

    if failed:
        yield ValidationError(f"{instance!r} is not a multiple of {dB}")


def not_(
    validator: Validator, not_schema: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if validator.evolve(schema=not_schema).is_valid(instance):
        message = f"{instance!r} should not be valid under {not_schema!r}"
        yield ValidationError(message)


def oneOf(
    validator: Validator, oneOf: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    subschemas = enumerate(oneOf)
    all_errors = []
    for index, subschema in subschemas:
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            f"{instance!r} is not valid under any of the given schemas",
            context=all_errors,
        )

    more_valid = [
        each
        for _, each in subschemas
        if validator.evolve(schema=each).is_valid(instance)
    ]
    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        yield ValidationError(f"{instance!r} is valid under each of {reprs}")


def pattern(
    validator: Validator, patrn: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "string"):
        return

    if not re.search(patrn, instance):
        yield ValidationError(f"{instance!r} does not match {patrn!r}")


def patternProperties(
    validator: Validator, patternProperties: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return

    for pattern, subschema in patternProperties.items():
        for k, v in instance.items():
            if not validator.is_type(k, "string"):
                continue
            if re.search(pattern, k):
                yield from validator.descend(
                    v,
                    subschema,
                    path=k,
                    schema_path=pattern,
                    property_path=k,
                )


def properties(
    validator: Validator, properties: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return

    for p, subschema in properties.items():
        # use the instance keys because it gives us the start_mark
        k = [k for k in instance.keys() if k == p]
        if p in instance:
            yield from validator.descend(
                instance[p],
                subschema,
                path=k[0] if len(k) > 0 else p,
                schema_path=p,
                property_path=k[0] if len(k) > 0 else p,
            )


def propertyNames(
    validator: Validator, propertyNames: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return

    for property in instance:
        yield from validator.descend(
            instance=property,
            schema=propertyNames,
            path=property,
            property_path="*",
        )


def ref(
    validator: Validator, ref: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    scope, resolved = validator.resolver.resolve(ref)
    validator.resolver.push_scope(scope)

    try:
        yield from validator.descend(instance, resolved)
    finally:
        validator.resolver.pop_scope()


def required(
    validator: Validator, required: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return
    for property in required:
        if property not in instance:
            yield ValidationError(f"{property!r} is a required property")


def requiredXor(
    validator: Validator, required: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if not validator.is_type(instance, "object"):
        return
    matches = set(required).intersection(instance.keys())
    if not matches:
        yield ValidationError(f"Only one of {required!r} is a required property")
        return
    if len(matches) > 1:
        for match in matches:
            yield ValidationError(
                f"Only one of {required!r} is a required property", path=[match]
            )


def uniqueItems(
    validator: Validator, uI: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if uI and validator.is_type(instance, "array") and not uniq(instance):
        yield ValidationError(f"{instance!r} has non-unique elements")


def uniqueKeys(
    validator: Validator, uKs: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    if uKs and validator.is_type(instance, "array") and not uniq_keys(instance, uKs):
        yield ValidationError(f"{instance!r} has non-unique elements for keys {uKs!r}")


def type(
    validator: Validator, tS: Any, instance: Any, schema: Dict[str, Any]
) -> ValidationResult:
    tS = ensure_list(tS)
    if not any(validator.is_type(instance, type) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")


def prefixItems(validator, prefixItems, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    for (index, item), subschema in zip(enumerate(instance), prefixItems):
        yield from validator.descend(
            instance=item,
            schema=subschema,
            schema_path=index,
            path=deque([index]),
            property_path=deque(["*"]),
        )
