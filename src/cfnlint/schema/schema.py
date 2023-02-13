"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from copy import deepcopy
from typing import Dict, List, Tuple

import jsonpatch

from cfnlint.schema._pointer import resolve_pointer

# Can't use a dataclass because its hard to parse in json
# with optional fields without addtional help


class Schema:
    _json_schema: Dict

    def __init__(self, schema) -> None:
        self.schema = deepcopy(schema)
        self._json_schema = self._cleanse_schema(schema=schema)
        self.type_name = schema["typeName"]

    def _cleanse_schema(self, schema) -> Dict:
        for ro_prop in schema.get("readOnlyProperties", []):
            sub_schema = schema
            for p in ro_prop.split("/")[1:-1]:
                sub_schema = sub_schema.get(p)
                if sub_schema is None:
                    break
            if sub_schema is not None:
                if sub_schema.get(ro_prop.split("/")[-1]) is not None:
                    del sub_schema[ro_prop.split("/")[-1]]

        return schema

    def json_schema(self) -> Dict:
        """Return the JSON Schema version of the CFN Schema

        Args:
        Returns:
            Dict: the JSON schema representation of the CFN schema
        """
        return self._json_schema

    def _flatten_getatts(self, ptr: str) -> Tuple[Dict[str, Dict], bool]:
        getatts = {}
        name = ".".join(ptr.split("/")[2:])
        obj = resolve_pointer(self.schema, ptr)
        is_object = False
        if "$ref" in obj:
            subs, sub_is_object = self._flatten_getatts(obj.get("$ref"))
            for sub_name, sub in subs.items():
                cp = deepcopy(obj)
                del cp["$ref"]
                cp.update(sub)
                if sub_is_object:
                    getatts[f"{name}.{sub_name}"] = cp
                else:
                    getatts[name] = cp
        elif obj.get("type") == "object":
            is_object = True
            for prop, value in obj.get("properties", {}).items():
                getatts[prop] = value
        else:
            getatts[name] = obj

        return getatts, is_object

    def patch(self, patches: List[Dict]) -> None:
        """Patches the schema file

        Args:
            patches: A list of JSON Patches
        Returns:
            None: Returns when the patches have been applied
        """
        jsonpatch.JsonPatch(patches).apply(self._json_schema, in_place=True)

    def get_atts(self) -> Dict[str, dict]:
        """Get the valid GetAtts for this schema. Schemas are defined in property
            readOnlyProperties and we need to build definitions of those properties

        Args:
        Returns:
            Dict[str, dict]: Dict of keys with valid strings and the json schema
            object for the property
        """
        attrs = {}
        for ro_attr in self.schema.get("readOnlyProperties", []):
            try:
                attrs.update(self._flatten_getatts(ro_attr)[0].items())
            except KeyError:
                pass

        return attrs
