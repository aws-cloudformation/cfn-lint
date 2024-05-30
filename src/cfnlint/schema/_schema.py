"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional

import jsonpatch

from cfnlint.schema._getatts import AttributeDict, GetAtts
from cfnlint.schema_resolver import RefResolver

# Can't use a dataclass because its hard to parse in json
# with optional fields without addtional help


class Schema:
    _json_schema: Dict

    def __init__(self, schema: Dict[str, Any], is_cached: bool = False) -> None:
        self.is_cached = is_cached
        self.schema = deepcopy(schema)
        self._json_schema = self._cleanse_schema(schema=deepcopy(schema))
        self.type_name = schema["typeName"]
        self._getatts = GetAtts(self.schema)
        self.resolver = RefResolver.from_schema(schema)

    def _cleanse_schema(self, schema: Dict[str, Any]) -> Dict:
        for ro_prop in schema.get("readOnlyProperties", []):
            sub_schema: Optional[Dict[str, Any]] = schema
            for p in ro_prop.split("/")[1:-1]:
                if not isinstance(sub_schema, dict):
                    raise ValueError(f"Should be an object for: {sub_schema!r}")
                sub_schema = sub_schema.get(p)
                if sub_schema is None:
                    break
            if sub_schema is not None:
                if sub_schema.get(ro_prop.split("/")[-1]) is not None:
                    del sub_schema[ro_prop.split("/")[-1]]

        return schema

    @property
    def json_schema(self) -> Dict:
        """Return the JSON Schema version of the CFN Schema

        Args:
        Returns:
            Dict: the JSON schema representation of the CFN schema
        """
        return self._json_schema

    def patch(self, patches: List[Dict]) -> None:
        """Patches the schema file

        Args:
            patches: A list of JSON Patches
        Returns:
            None: Returns when the patches have been applied
        """
        jsonpatch.JsonPatch(patches).apply(self._json_schema, in_place=True)

    @property
    def get_atts(self) -> AttributeDict:
        """Get the valid GetAtts for this schema. Schemas are defined in property
            readOnlyProperties and we need to build definitions of those properties

        Args:
        Returns:
            Dict[str, GetAtt]: Dict of keys with valid strings and the json schema
            object for the property
        """
        return self._getatts.attrs
