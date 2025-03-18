"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from copy import deepcopy

from cfnlint.decode.mark import Mark

LOGGER = logging.getLogger(__name__)


def create_str_node_class(cls):
    """
    Create string node class
    """

    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(
            self, x, start_mark: Mark | None = None, end_mark: Mark | None = None
        ):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)

            self.start_mark = start_mark or Mark()
            self.end_mark = end_mark or Mark()

        # pylint: disable=bad-classmethod-argument, unused-argument
        def __new__(self, x, start_mark, end_mark):
            return cls.__new__(self, x)

        def __deepcopy__(self, memo):
            result = str_node(self, self.start_mark, self.end_mark)
            memo[id(self)] = result
            return result

    node_class.__name__ = f"{cls.__name__}_node"
    return node_class


def create_dict_node_class(cls):
    """
    Create dynamic node class
    """

    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(
            self,
            x,
            start_mark: Mark | None = None,
            end_mark: Mark | None = None,
            using_merge: bool = False,
        ):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark or Mark()
            self.end_mark = end_mark or Mark()
            self.using_merge = using_merge

        def __deepcopy__(self, memo):
            result = dict_node(self, self.start_mark, self.end_mark)
            memo[id(self)] = result
            for k, v in self.items():
                result[deepcopy(k)] = deepcopy(v, memo)

            return result

        def get(self, key, default=None):
            """Override the default get"""
            if isinstance(default, dict):
                default = dict_node(default, self.start_mark, self.end_mark)
            return super().get(key, default)

    node_class.__name__ = f"{cls.__name__}_node"
    return node_class


def create_dict_list_class(cls):
    """
    Create dynamic list class
    """

    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(
            self, x, start_mark: Mark | None = None, end_mark: Mark | None = None
        ):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark or Mark()
            self.end_mark = end_mark or Mark()

        def __deepcopy__(self, memo):
            result = list_node([], self.start_mark, self.end_mark)
            memo[id(self)] = result
            for _, v in enumerate(self):
                result.append(deepcopy(v, memo))

            return result

    node_class.__name__ = f"{cls.__name__}_node"
    return node_class


str_node = create_str_node_class(str)
dict_node = create_dict_node_class(dict)
list_node = create_dict_list_class(list)
