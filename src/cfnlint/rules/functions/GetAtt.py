"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Sequence

import regex as re

from cfnlint.helpers import ensure_list, is_types_compatible
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER


class GetAtt(BaseFn):
    """Check if GetAtt values are correct"""

    id = "E1010"
    shortdesc = "GetAtt validation of parameters"
    description = (
        "Validates that GetAtt parameters are to valid resources and properties of"
        " those resources"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "getatt"]

    def __init__(self) -> None:
        super().__init__("Fn::GetAtt", all_types)

    def schema(self, validator, instance) -> dict[str, Any]:
        resource_functions = []
        if validator.context.transforms.has_language_extensions_transform():
            resource_functions = ["Ref"]

        return {
            "type": ["string", "array"],
            "minItems": 2,
            "maxItems": 2,
            "fn_items": [
                {
                    "functions": resource_functions,
                    "schema": {
                        "type": ["string"],
                    },
                },
                {
                    "functions": ["Ref"],
                    "schema": {
                        "type": ["string"],
                    },
                },
            ],
        }

    def _resolve_getatt(
        self,
        validator: Validator,
        key: str,
        value: Any,
        instance: Any,
        s: Any,
        paths: Sequence[Any],
    ) -> ValidationResult:

        for resource_name, resource_name_validator, _ in validator.resolve_value(
            value[0]
        ):
            for err in self.fix_errors(
                resource_name_validator.descend(
                    resource_name,
                    {"enum": list(validator.context.resources.keys())},
                    path=key,
                )
            ):
                err.path.append(paths[0])
                if err.instance != value[0]:
                    err.message = err.message + f" when {value[0]!r} is resolved"
                yield err
                break
            else:
                t = validator.context.resources[resource_name].type
                for (
                    regions,
                    schema,
                ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
                    t, validator.context.regions
                ):
                    region = regions[0]
                    for attribute_name, _, _ in validator.resolve_value(value[1]):
                        if all(
                            not (bool(re.fullmatch(each, attribute_name)))
                            for each in validator.context.resources[
                                resource_name
                            ].get_atts(region)
                        ):
                            err = ValidationError(
                                (
                                    f"{attribute_name!r} is not one of "
                                    f"{validator.context.resources[resource_name].get_atts(region)!r}"
                                    f" in {regions!r}"
                                ),
                                validator=self.fn.py,
                                path=deque([self.fn.name, 1]),
                            )
                            if attribute_name != value[1]:
                                err.message = (
                                    err.message + f" when {value[1]!r} is resolved"
                                )
                            yield err
                            continue

                        evolved = validator.evolve(schema=s)  # type: ignore
                        evolved.validators = {  # type: ignore
                            "type": validator.validators.get("type"),  # type: ignore
                        }

                        getatts = validator.cfn.get_valid_getatts()
                        t = validator.context.resources[resource_name].type
                        pointer = getatts.match(region, [resource_name, attribute_name])

                        getatt_schema = schema.resolver.resolve_cfn_pointer(pointer)
                        if not getatt_schema.get("type") or not s.get("type"):
                            continue

                        schema_types = ensure_list(getatt_schema.get("type"))
                        types = ensure_list(s.get("type"))

                        if is_types_compatible(
                            types, schema_types, validator.context.strict_types
                        ):
                            continue

                        reprs = ", ".join(repr(type) for type in types)
                        yield ValidationError(
                            (f"{instance!r} is not of type {reprs}"),
                            validator=self.fn.py,
                            path=deque([self.fn.name]),
                            schema_path=deque(["type"]),
                        )

    def fn_getatt(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        key, value = self.key_value(instance)
        paths: list[int | None] = [0, 1]
        if validator.is_type(value, "string"):
            paths = [None, None]
            value = value.split(".", 1)

        errs = list(
            self._resolve_getatt(
                self.validator(validator), key, value, instance, s, paths
            )
        )
        if errs:
            yield from iter(errs)
            return

        keyword = validator.context.path.cfn_path_string
        for rule in self.child_rules.values():
            if rule is None:
                continue
            if keyword in rule.keywords or "*" in rule.keywords:  # type: ignore
                yield from rule.validate(validator, s, value, s)  # type: ignore
