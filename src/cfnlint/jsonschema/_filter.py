"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from dataclasses import dataclass, field, fields

# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from typing import Any, Sequence

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

    def filter(self, validator: Any, instance: Any, schema: Any):
        if validator.is_type(instance, "object"):
            if len(instance) == 1:
                k = list(instance.keys())[0]
                if k in self.functions:
                    k_py = ToPy(k)
                    yield (instance.get(k), {k_py.py: schema})
                    return

        yield (instance, schema)

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
