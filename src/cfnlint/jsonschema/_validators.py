"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Originally taken from https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_validators.py
and https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_legacy_validators.py
adapted for CloudFormation usage
"""
from copy import deepcopy

import regex as re
from jsonschema._utils import ensure_list, find_additional_properties

from cfnlint.helpers import (
    FUNCTIONS_MULTIPLE,
    FUNCTIONS_SINGLE,
    PSEUDOPARAMS_MULTIPLE,
    PSEUDOPARAMS_SINGLE,
)
from cfnlint.jsonschema._utils import equal as s_equal
from cfnlint.jsonschema._utils import unbool
from cfnlint.jsonschema.exceptions import ValidationError

_singular_types = ["string", "boolean", "number", "integer"]
_multiple_types = ["array"]


def additionalProperties(validator, aP, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    extras = set(find_additional_properties(instance, schema))

    if validator.is_type(aP, "object"):
        for extra in extras:
            yield from validator.descend(instance[extra], aP, path=extra)
    elif not aP and extras:
        if "patternProperties" in schema:
            if len(extras) == 1:
                verb = "does"
            else:
                verb = "do"

            joined = ", ".join(repr(each) for each in sorted(extras))
            patterns = ", ".join(
                repr(each) for each in sorted(schema["patternProperties"])
            )
            error = f"{joined} {verb} not match any of the regexes: {patterns}"
            yield ValidationError(error)
        else:
            for extra in extras:
                error = "Additional properties are not allowed (%s unexpected)"
                yield ValidationError(error % extra, path=[extra])


# pylint: disable=unused-argument
def exclusiveMinimum(validator, m, instance, schema):
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
            f"{instance!r} is less than or equal to " f"the minimum of {m!r}",
        )


# pylint: disable=unused-argument
def exclusiveMaximum(validator, m, instance, schema):
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
            f"{instance!r} is greater than or equal " f"to the maximum of {m!r}",
        )


# pylint: disable=unused-argument
def minItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) < mI:
        yield ValidationError(f"{instance!r} is too short")


# pylint: disable=unused-argument
def maxItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) > mI:
        yield ValidationError(f"{instance!r} is too long")


# pylint: disable=unused-argument
def minimum(validator, m, instance, schema):
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


# pylint: disable=unused-argument
def maximum(validator, m, instance, schema):
    t_instance = deepcopy(instance)
    if validator.is_type(t_instance, "string"):
        try:
            t_instance = float(t_instance)
        except:  # pylint: disable=bare-except
            return
    if not validator.is_type(t_instance, "number"):
        return

    if t_instance > m:
        message = f"{instance!r} is greater than the maximum of {m!r}"
        yield ValidationError(message)


# pylint: disable=unused-argument
def pattern(validator, patrn, instance, schema):
    if validator.is_type(instance, "string") and not re.search(patrn, instance):
        yield ValidationError(f"{instance!r} does not match {patrn!r}")


# pylint: disable=unused-argument
def enum(validator, enums, instance, schema):
    if instance in (0, 1):
        unbooled = unbool(instance)
        if all(not (s_equal(unbooled, unbool(each))) for each in enums):
            yield ValidationError(f"{instance!r} is not one of {enums!r}")
    else:
        if all(not (s_equal(instance, each)) for each in enums):
            yield ValidationError(f"{instance!r} is not one of {enums!r}")


def _cfn_type(validator, tS, instance, schema):
    reprs = ", ".join(repr(type) for type in tS)

    if any(validator.is_type(instance, type) for type in ["object", "array"]):
        yield ValidationError(
            f"{instance!r} is not of type {reprs}",
            extra_args={},
        )
        return
    if "string" in tS:
        return
    if "number" in tS:
        try:
            float(instance)
            return
        except ValueError:
            pass
    if "integer" in tS:
        if isinstance(instance, float):
            yield ValidationError(
                f"{instance!r} is not of type {reprs}",
                extra_args={},
            )
            return
        try:
            int(instance)
            return
        except ValueError:
            pass
    if "boolean" in tS:
        if instance in ["true", "false"]:
            return
    yield ValidationError(
        f"{instance!r} is not of type {reprs}",
        extra_args={},
    )


# pylint: disable=unused-argument,redefined-builtin
def cfn_type(validator, tS, instance, schema):
    """
    When evaluating a type in CloudFormation we have to account
    for the intrinsic functions that the values can represent
    (Ref, GetAtt, If, ...).  This will evaluate if the correct type
    is not found and the instance is an object with a function
    that we do our best to evaluate if that function represents the
    type we are looking for
    """
    tS = ensure_list(tS)
    reprs = ", ".join(repr(type) for type in tS)
    if not any(validator.is_type(instance, type) for type in tS):
        if validator.is_type(instance, "object"):
            if len(instance) == 1:
                k = next(iter(instance), "")
                v = instance.get(k, [])
                if k == "Fn::If":
                    if len(v) == 3:
                        for i in range(1, 3):
                            for v_err in cfn_type(
                                validator=validator,
                                tS=tS,
                                instance=v[i],
                                schema=schema,
                            ):
                                v_err.path.append("Fn::If")
                                v_err.path.append(i)
                                yield v_err
                    return
                if k == "Ref":
                    if "array" in tS:
                        if v in PSEUDOPARAMS_SINGLE:
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}",
                                extra_args={},
                            )
                    if any(type in _singular_types for type in tS):
                        if v in PSEUDOPARAMS_MULTIPLE:
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}",
                                extra_args={},
                            )
                    return
                if k in FUNCTIONS_MULTIPLE:
                    if "array" in tS:
                        return
                    yield ValidationError(
                        f"{instance!r} is not of type {reprs}", extra_args={}
                    )
                elif k in FUNCTIONS_SINGLE:
                    if any(type in _singular_types for type in tS):
                        return
                    yield ValidationError(
                        f"{instance!r} is not of type {reprs}", extra_args={}
                    )
                else:
                    yield from _cfn_type(validator, tS, instance, schema)
                return

        yield from _cfn_type(validator, tS, instance, schema)


# pylint: disable=unused-argument,redefined-builtin
def type(validator, tS, instance, schema):
    """
    Standard type checking for when we are looking at strings
    that are JSON (IAM Policy, Step Functions, ...)
    """
    tS = ensure_list(tS)

    if not any(validator.is_type(instance, type) for type in tS):
        reprs = ", ".join(repr(type) for type in tS)
        yield ValidationError(f"{instance!r} is not of type {reprs}")
