"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from dataclasses import dataclass, field, fields
from typing import Any, Sequence, Tuple

from cfnlint.helpers import ToPy
from cfnlint.jsonschema._utils import ensure_list

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
            "required",
            "requiredXor",
            "requiredAtLeastOne",
            "dependentExcluded",
            "dependentRequired",
            "minItems",
            "minProperties",
            "maxItems",
            "maxProperties",
            "uniqueItems",
        ],
    )

    def _filter_schemas(self, schema, validator: Any) -> Tuple[Any, Any]:
        """
        Filter the schemas to only include the ones that are required
        """
        if validator.cfn is None:
            return schema, None
        if not any(fn in ["Ref", "Fn::If"] for fn in validator.context.functions):
            return schema, None
        standard_schema = {}
        group_schema = {}
        for key, value in schema.items():
            if key in self.group_functions:
                group_schema[key] = value
            else:
                standard_schema[key] = value

        # some times CloudFormation dumps to standard nested "json".
        # it will do by using {"type": "object"} with no properties
        # Adding these items to the schema
        # will allow us to continue to check the nested elements
        if "awsType" not in standard_schema:
            if (
                "object" in ensure_list(standard_schema.get("type", []))
                and "properties" not in standard_schema
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

    def filter(self, validator: Any, instance: Any, schema: Any):
        # dependencies, required, minProperties, maxProperties
        # need to have filtered properties to validate
        # because of Ref: AWS::NoValue

        standard_schema, group_schema = self._filter_schemas(schema, validator)

        if group_schema:
            scenarios = validator.cfn.get_object_without_conditions(instance)
            for scenario in scenarios:
                yield (scenario.get("Object"), group_schema)

        if validator.is_type(instance, "object"):
            if len(instance) == 1:
                for k, v in instance.items():
                    if k in validator.context.functions:
                        k_py = ToPy(k)
                        k_schema = {
                            k_py.py: standard_schema,
                        }
                        yield (instance, k_schema)
                        return
                    if validator.is_type(k, "string") and k.startswith("Fn::ForEach::"):
                        k_py = ToPy("Fn::ForEach")
                        k_schema = {
                            k_py.py: standard_schema,
                        }
                        yield ({k: v}, k_schema)
                        return
                else:
                    yield (instance, standard_schema)
                return
            for k, v in instance.items():
                # Fn::ForEach can be supported at the same level as more Fn::ForEach
                # and other keys
                if not validator.is_type(k, "string"):
                    continue
                if k.startswith("Fn::ForEach::"):
                    k_py = ToPy("Fn::ForEach")
                    k_schema = {
                        k_py.py: standard_schema,
                    }
                    yield ({k: v}, k_schema)

        yield (instance, standard_schema)

    def evolve(self, **kwargs) -> "FunctionFilter":
        """
        Create a new context merging together attributes
        """
        cls = self.__class__
        for f in fields(FunctionFilter):
            if f.init:
                kwargs.setdefault(f.name, getattr(self, f.name))

        return cls(**kwargs)
