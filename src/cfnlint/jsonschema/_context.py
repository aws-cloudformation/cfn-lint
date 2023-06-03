"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from collections import deque
from typing import Any, Callable, Deque, Dict, Iterable, Sequence

import attr

from cfnlint.helpers import REGION_PRIMARY
from cfnlint.jsonschema.exceptions import ValidationError

V = Callable[[Any, Any, Any, Dict[str, Any]], Iterable[ValidationError]]


@attr.s(frozen=False, repr=False)
class Context:
    """
    A :kw:`type` property checker.

    A `Context` keeps track of the current context that we are evaluating against
    Arguments:

        region:

            The region being evaluated against.

        conditions:

            The conditions being used and their current state
    """

    region: Sequence[str] = attr.ib(default=REGION_PRIMARY)
    conditions: Dict[str, bool] = attr.ib(attr.Factory(dict))
    path: Deque[str] = attr.ib(attr.Factory(deque))

    def evolve(self, **kwargs) -> "Context":
        """
        Create a new context merging together attributes
        """
        cls = self.__class__
        kwargs.setdefault("region", self.region)

        if "conditions" in kwargs:
            kwargs["conditions"].update(self.conditions.copy())
        else:
            kwargs["conditions"] = self.conditions.copy()
        if "path" in kwargs:
            kwargs["path"].extendleft(self.path)
        else:
            kwargs["path"] = self.path.copy()

        return cls(**kwargs)
