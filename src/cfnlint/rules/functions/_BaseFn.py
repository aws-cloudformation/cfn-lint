"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import namedtuple
from typing import Any, Dict, List, Tuple

from cfnlint.helpers import ToPy
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule

SchemaDetails = namedtuple("SchemaDetails", ["module", "filename"])
all_types = ("array", "boolean", "integer", "number", "object", "string")
singular_types = ("boolean", "integer", "number", "string")


class BaseFn(CloudFormationLintRule):
    def __init__(
        self,
        name: str = "",
        types: Tuple[str, ...] | None = None,
        functions: Tuple[str, ...] | None = None,
    ) -> None:
        super().__init__()
        self.fn = ToPy(name)
        self.types = types or tuple([])
        self.functions = functions or tuple([])

    def key_value(self, instance: Dict[str, Any]) -> Tuple[str, Any]:
        return list(instance.keys())[0], instance.get(self.fn.name)

    def fix_errors(self, errs: ValidationResult) -> ValidationResult:
        for err in errs:
            if err.validator not in ["ref"]:  # fix the list to all validators
                err.validator = self.fn.py
            yield err

    def schema(self, validator: Validator, instance: Any) -> Dict[str, Any]:
        return {
            "type": ["string"],
        }

    def validator(self, validator: Validator) -> Validator:
        return validator.evolve(
            context=validator.context.evolve(functions=self.functions),
        )

    def get_keyword(self, validator: Validator) -> str:
        if len(validator.context.path) < 1:
            return ""

        if (
            validator.context.path[0] not in ["Resources", "Parameters"]
            or len(validator.context.path) < 2
        ):
            return "/".join(str(i) for i in validator.context.path)

        if validator.context.path[0] == "Resources":
            resource_name = validator.context.path[1]
            if resource_name in validator.context.resources:
                resource_type = validator.context.resources[resource_name].type
                return "/".join(
                    ["Resources", resource_type]
                    + list(x for x in validator.context.path if isinstance(x, str))[2:]
                )

        if validator.context.path[0] == "Parameters":
            parameter_name = validator.context.path[1]
            if parameter_name in validator.context.parameters:
                parameter_type = validator.context.parameters[parameter_name].type
                return "/".join(
                    ["Parameters", parameter_type]
                    + list(x for x in validator.context.path if isinstance(x, str))[2:]
                )

        return ""

    def resolve(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        key, _ = self.key_value(instance)

        for value, v, resolve_err in validator.resolve_value(instance):
            if resolve_err:
                yield resolve_err
                continue
            for err in self.fix_errors(v.descend(value, s, key)):
                err.message = err.message.replace(f"{value!r}", f"{instance!r}")
                err.message = f"{err.message} when {self.fn.name!r} is resolved"
                yield err

    def resolve_type(self, validator, schema) -> List[str]:
        if "type" in schema:
            return ensure_list(schema["type"])  # type: ignore

        if "$ref" in schema:
            resolve = getattr(validator.resolver, "resolve", None)
            ref = schema["$ref"]
            if resolve is None:
                resolved = validator.resolver.resolving(ref)
            else:
                _, resolved = validator.resolver.resolve(ref)

            if "type" in resolved:
                return ensure_list(resolved["type"])  # type: ignore

        return []

    def validate_fn_output_types(
        self, validator: Validator, s: Any, instance: Any
    ) -> ValidationResult:
        tS = self.resolve_type(validator, s)
        if tS:
            if not any(t in self.types for t in tS):
                reprs = ", ".join(repr(type) for type in tS)
                yield ValidationError(f"{instance!r} is not of type {reprs}")

    def validate(
        self,
        validator: Validator,
        s: Any,
        instance: Any,
        schema: Any,
    ) -> ValidationResult:
        # validate this function will return the correct type
        errs = list(
            self.fix_errors(self.validate_fn_output_types(validator, s, instance))
        )

        key, value = self.key_value(instance)
        errs.extend(
            list(
                self.fix_errors(
                    self.validator(validator).descend(
                        value, self.schema(validator, instance), path=key
                    )
                )
            )
        )

        if errs:
            yield from iter(errs)
            return

        yield from self.resolve(validator, s, instance, schema)
