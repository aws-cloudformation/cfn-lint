"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Dict

import jsonpatch

from cfnlint.schema._getatts import AttributeDict, GetAtts
from cfnlint.schema.resolver import RefResolver

# Can't use a dataclass because its hard to parse in json
# with optional fields without addtional help


class Schema:
    def __init__(self, schema: dict[str, Any], is_cached: bool = False) -> None:
        self.is_cached: bool = is_cached
        self._schema: dict[str, Any] = schema
        self._type_name: str = schema["typeName"]
        self.resolver: RefResolver = RefResolver.from_schema(schema)
        self._getatts: GetAtts = GetAtts(self)

    @property
    def type_name(self) -> str:
        """Return the type name of the schema"""
        return self._type_name

    @property
    def schema(self) -> Dict:
        """Return the JSON Schema version of the CFN Schema

        Args:
        Returns:
            Dict: the JSON schema representation of the CFN schema
        """
        return self._schema

    def patch(self, patches: list[Dict]) -> None:
        """Patches the schema file

        Args:
            patches: A list of JSON Patches
        Returns:
            None: Returns when the patches have been applied
        """
        jsonpatch.JsonPatch(patches).apply(self.schema, in_place=True)

    @property
    def get_atts(self) -> AttributeDict:
        """Get the valid GetAtts for this schema. Schemas are defined in property
            readOnlyProperties and we need to build definitions of those properties

        Args:
        Returns:
            dict[str, GetAtt]: Dict of keys with valid strings and the json schema
            object for the property
        """
        return self._getatts.attrs
