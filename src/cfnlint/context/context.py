"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from collections import deque
from typing import Deque, Dict, Sequence

import attr

from cfnlint.context.value import Value
from cfnlint.helpers import REGION_PRIMARY


@attr.s(frozen=False, repr=False)
class Context:
    """
    A `Context` keeps track of the current context that we are evaluating against
    Arguments:

        region:

            The region being evaluated against.

        conditions:

            The conditions being used and their current state
    """

    # what region we are processing
    region: Sequence[str] = attr.ib(default=REGION_PRIMARY)

    # As we move down the template this is used to keep track of the
    # how the conditions affected the path we are on
    # The key is the condition name and the value is if the condition
    # was true or false
    conditions: Dict[str, bool] = attr.ib(attr.Factory(dict))

    # path keeps track of the path as we move down the template
    # Example: Resources, MyResource, Properties, Name, ...
    path: Deque[str] = attr.ib(attr.Factory(deque))

    # The value if we are processing a value. Usually is none
    # but when we process a function the value could be the
    # result of the function being called
    value: Value = attr.ib(default=None)

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

        if "path" in kwargs and kwargs["path"]:
            new_path = self.path.copy()
            new_path.extend(kwargs["path"])
            kwargs["path"] = new_path
        else:
            kwargs["path"] = self.path.copy()

        return cls(**kwargs)
