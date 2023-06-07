"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from dataclasses import dataclass, field, fields

# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from typing import Any, Sequence, Tuple

from cfnlint.helpers import FUNCTIONS, ToPy


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

    functions: Sequence[str] = field(default_factory=list)
    group_functions: Sequence[str] = field(
        init=False,
        default_factory=lambda: [
            "dependencies",
            "required",
            "minProperties",
            "maxProperties",
            "uniqueItems",
        ],
    )

    def _filter_schemas(self, schema, validator) -> Tuple[Any, Any]:
        """
        Filter the schemas to only include the ones that are required
        """
        if validator.cfn is None:
            return schema, None
        standard_schema = {}
        group_schema = {}
        for key, value in schema.items():
            if key in self.group_functions:
                group_schema[key] = value
            else:
                standard_schema[key] = value

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
                k = list(instance.keys())[0]
                if k in self.functions:
                    k_py = ToPy(k)
                    yield (instance, {k_py.py: standard_schema})
                    return

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


cfn_function_filter = FunctionFilter(list(FUNCTIONS))  # type: ignore
standard_function_filter = FunctionFilter(list([]))  # type: ignore
