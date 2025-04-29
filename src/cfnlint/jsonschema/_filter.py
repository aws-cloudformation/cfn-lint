"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING, Any, Iterator, Sequence, Tuple

from cfnlint.helpers import FUNCTIONS, REGEX_DYN_REF, ToPy, ensure_list

if TYPE_CHECKING:
    from cfnlint.jsonschema.protocols import Validator

_all_types = ["array", "boolean", "integer", "number", "object", "string"]


@dataclass
class FunctionFilter:
    """
    A :kw:`type` property checker.

    A `FunctionChecker` looks for CloudFormation functions and resolves them
    as it can. There are scenarios where the value cannot be fully resolved
    and in that case nothing will happen

    Arguments:

        type_checkers:

            The initial mapping of types to their checking functions.
    """

    group_functions: Sequence[str] = field(
        init=False,
        default_factory=lambda: [
            "dependencies",
            "dependentExcluded",
            "dependentRequired",
            "else",
            "if",
            "maxItems",
            "maxProperties",
            "minItems",
            "minProperties",
            "required",
            "requiredOr",
            "requiredXor",
            "then",
            "uniqueItems",
        ],
    )

    add_cfn_lint_keyword: bool = field(
        init=True,
        default=True,
    )

    validate_dynamic_references: bool = field(
        init=True,
        default=True,
    )

    def _filter_schemas(self, schema, validator: Validator) -> Tuple[Any, Any]:
        """
        Filter the schemas to only include the ones that are required
        """

        # If we are in an if we want to keep any !Ref AWS::NoValue
        # Example: Typically we want to remove (!Ref AWS::NoValue)
        # to count minItems, maxItems, required properties but if we
        # are in an If we need to be more strict
        if validator.context.path.path:
            if validator.context.path.path[-1] in ["Fn::If"]:
                return schema, None

        standard_schema = {}
        group_schema = {}
        for key, value in schema.items():
            if key in self.group_functions:
                group_schema[key] = value
            else:
                standard_schema[key] = value
        if self.add_cfn_lint_keyword and "$ref" not in standard_schema:
            standard_schema["cfnLint"] = ensure_list(standard_schema.get("cfnLint", []))
            standard_schema["cfnLint"].append("/".join(validator.context.path.cfn_path))

        # some times CloudFormation dumps to standard nested "json".
        # it will do by using {"type": "object"} with no properties
        # Adding these items to the schema
        # will allow us to continue to check the nested elements
        # If we have the cfnLint keyword we assume that another check will
        # take care of this for us
        if "object" in ensure_list(standard_schema.get("type", [])) and all(
            p not in standard_schema
            for p in ["properties", "additionalProperties", "patternProperties"]
        ):
            standard_schema["patternProperties"] = {
                ".*": {"type": _all_types},
            }
        if (
            "array" in standard_schema.get("type", [])
            and "items" not in standard_schema
        ):
            standard_schema["items"] = {"type": _all_types}

        return standard_schema, group_schema

    def filter(
        self, validator: Any, instance: Any, schema: Any
    ) -> Iterator[tuple[Any, dict[str, Any], "Validator"]]:
        # if cfnContext is in the schema it is singular and
        # needs to be processed first
        if any(s in schema for s in ["cfnContext"]):
            yield instance, schema, validator
            return

        # Lets validate dynamic references when appropriate
        if validator.is_type(instance, "string") and self.validate_dynamic_references:
            if REGEX_DYN_REF.findall(instance):
                # if we are in a function we can't validate
                # dynamic references the same way
                if not any(
                    p in set(FUNCTIONS) - set(["Fn::If"])
                    for p in validator.context.path.path
                ):
                    yield (instance, {"dynamicReference": schema}, validator)
                    return
                return

        # if there are no functions then we don't need to worry
        # about ref AWS::NoValue or If conditions
        if not validator.context.functions:
            yield instance, schema, validator
            return

        # dependencies, required, minProperties, maxProperties
        # need to have filtered properties to validate
        # because of Ref: AWS::NoValue
        standard_schema, group_schema = self._filter_schemas(schema, validator)

        if group_schema:
            for (
                scenario_instance,
                scenario,
            ) in validator.context.conditions.evolve_from_instance(
                instance,
                context=validator.context,
            ):
                if scenario_instance is None:
                    continue
                scenario_validator = validator.evolve(
                    context=validator.context.evolve(conditions=scenario)
                )
                yield (scenario_instance, group_schema, scenario_validator)

        if validator.is_type(instance, "object"):
            if len(instance) == 1:
                for k, v in instance.items():
                    if k in validator.context.functions:
                        k_py = ToPy(k)
                        k_schema = {
                            k_py.py: standard_schema,
                        }
                        yield (instance, k_schema, validator)
                        return

        yield (instance, standard_schema, validator)

    def evolve(self, **kwargs) -> "FunctionFilter":
        """
        Create a new context merging together attributes
        """
        cls = self.__class__
        for f in fields(FunctionFilter):
            if f.init:
                kwargs.setdefault(f.name, getattr(self, f.name))

        return cls(**kwargs)
