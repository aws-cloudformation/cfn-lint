"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import (
    PSEUDOPARAMS_MULTIPLE,
    PSEUDOPARAMS_SINGLE,
    VALID_PARAMETER_TYPES,
    VALID_PARAMETER_TYPES_LIST,
)
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class Ref(BaseFn):
    id = "E1020"
    shortdesc = "Ref validation of value"
    description = (
        "Making sure the Ref has a String value (no other functions are supported)"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html"
    tags = ["functions", "ref"]

    def __init__(self) -> None:
        super().__init__(
            "Ref",
            all_types,
            resolved_rule="W1030",
        )
        self._all_refs = [
            "W2010",
        ]
        self.child_rules.update(dict.fromkeys(self._all_refs))

    def ref(
        self,
        validator: Validator,
        subschema: Any,
        instance: Any,
        schema: dict[str, Any],
    ):
        yield from super().validate(validator, subschema, instance, schema)

        _, value = self.key_value(instance)
        if not validator.is_type(value, "string"):
            return

        if value in validator.context.parameters:
            parameter_type = validator.context.parameters[value].type
            schema_types = self.resolve_type(validator, subschema)
            if not schema_types:
                return
            reprs = ", ".join(repr(type) for type in schema_types)

            if all(
                st not in ["string", "boolean", "integer", "number"]
                for st in schema_types
            ):
                if parameter_type not in VALID_PARAMETER_TYPES_LIST:
                    yield ValidationError(f"{instance!r} is not of type {reprs}")
                    return
            elif all(st not in ["array"] for st in schema_types):
                if parameter_type not in [
                    x
                    for x in VALID_PARAMETER_TYPES
                    if x not in VALID_PARAMETER_TYPES_LIST
                ]:
                    yield ValidationError(f"{instance!r} is not of type {reprs}")
                    return

        elif value in PSEUDOPARAMS_SINGLE or value in PSEUDOPARAMS_MULTIPLE:
            # Pseudo parameters resolve to a known type: the SINGLE set are
            # strings, PSEUDOPARAMS_MULTIPLE (AWS::NotificationARNs) is a list.
            # Validate that resolved type against the schema, the same way we
            # do for named parameters.
            schema_types = self.resolve_type(validator, subschema)
            if not schema_types:
                return
            reprs = ", ".join(repr(type) for type in schema_types)
            is_list = value in PSEUDOPARAMS_MULTIPLE

            if all(
                st not in ["string", "boolean", "integer", "number"]
                for st in schema_types
            ):
                if not is_list:
                    yield ValidationError(f"{instance!r} is not of type {reprs}")
                    return
            elif all(st not in ["array"] for st in schema_types):
                if is_list:
                    yield ValidationError(f"{instance!r} is not of type {reprs}")
                    return

        elif value in validator.context.resources:
            # A Ref to a resource always resolves to a string (the resource's
            # physical id/name), so it can satisfy a scalar slot but never an
            # object or array slot. Validate that against the schema the same
            # way we do for named and pseudo parameters. This catches a bare
            # Ref to a resource standing in for a whole object (e.g. an
            # UpdatePolicy/CreationPolicy value) without blanking the resource
            # map, which would break legitimate leaf Refs to resources.
            schema_types = self.resolve_type(validator, subschema)
            if not schema_types:
                return
            reprs = ", ".join(repr(type) for type in schema_types)
            if all(
                st not in ["string", "boolean", "integer", "number"]
                for st in schema_types
            ):
                yield ValidationError(f"{instance!r} is not of type {reprs}")
                return

        for rule_id in self._all_refs:
            rule = self.child_rules.get(rule_id)
            if rule:
                yield from rule.validate(validator, {}, value, subschema)  # type: ignore[attr-defined]

        keyword = validator.context.path.cfn_path_string
        for rule in self.child_rules.values():
            if not rule or rule.id in self._all_refs:
                continue
            if not hasattr(rule, "keywords"):
                continue
            if keyword in rule.keywords or "*" in rule.keywords:  # type: ignore[attr-defined]
                yield from rule.validate(validator, keyword, value, subschema)  # type: ignore[attr-defined]
