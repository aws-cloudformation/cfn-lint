"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterator

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Mappings:
    """
    This class holds a mapping
    """

    maps: dict[str, Map] = field(init=True, default_factory=dict)
    is_transform: bool = field(init=True, default=False)

    @classmethod
    def create_from_dict(cls, instance: Any) -> Mappings:

        if not isinstance(instance, dict):
            return cls({})
        try:
            result = {}
            is_transform = False
            for k, v in instance.items():
                if k == "Fn::Transform":
                    is_transform = True
                elif isinstance(k, str):
                    result[k] = Map.create_from_dict(v)
            return cls(result, is_transform)
        except (ValueError, AttributeError) as e:
            LOGGER.debug(e, exc_info=True)
            return cls({})


@dataclass(frozen=True)
class _MappingSecondaryKey:
    """
    This class holds a mapping value
    """

    keys: dict[str, list[Any] | str | int | float] = field(
        init=True, default_factory=dict
    )
    is_transform: bool = field(init=True, default=False)

    def value(self, secondary_key: str):
        if secondary_key not in self.keys:
            raise KeyError(secondary_key)
        return self.keys[secondary_key]

    @classmethod
    def create_from_dict(cls, instance: Any) -> _MappingSecondaryKey:
        if not isinstance(instance, dict):
            return cls({})
        is_transform = False
        keys = {}
        for k, v in instance.items():
            if k == "Fn::Transform":
                is_transform = True
            elif isinstance(k, str) and isinstance(v, (str, list, int, float)):
                keys[k] = v
        return cls(keys, is_transform)


@dataclass(frozen=True)
class Map:
    """
    This class holds a mapping
    """

    keys: dict[str, _MappingSecondaryKey] = field(init=True, default_factory=dict)
    is_transform: bool = field(init=True, default=False)

    def find_in_map(self, top_key: str, secondary_key: str) -> Iterator[Any]:
        if top_key not in self.keys:
            raise KeyError(top_key)
        yield self.keys[top_key].value(secondary_key)

    @classmethod
    def create_from_dict(cls, instance: Any) -> Map:
        if not isinstance(instance, dict):
            return cls({})
        is_transform = False
        keys = {}
        for k, v in instance.items():
            if k == "Fn::Transform":
                is_transform = True
            elif isinstance(k, str):
                keys[k] = _MappingSecondaryKey.create_from_dict(v)
        return cls(keys, is_transform)
