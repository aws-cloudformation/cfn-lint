from __future__ import annotations

from collections import UserDict
from typing import Any

from cfnlint.context import Resource
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, AttributeDict, ResourceNotFoundError


class _ResourceDict(UserDict):
    def __init__(self, __dict: None = None) -> None:
        self._has_modules: bool = False
        super().__init__(__dict)
        self.data: dict[str, AttributeDict] = {}

    def __setitem__(self, key: str, item: AttributeDict) -> None:
        if key.endswith(".*"):
            self._has_modules = True
        return super().__setitem__(key, item)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key: str) -> AttributeDict:
        attr = self.data.get(key)
        if attr is not None:
            return attr
        if not self._has_modules:
            raise KeyError(key)
        l_key = ""  # longest key
        for k in self.data.keys():
            if not k.endswith(".*"):
                continue
            if key.startswith(k[:-2]):
                if len(k) > len(l_key):
                    l_key = k
        if l_key:
            attr = self.data.get(l_key)
            if attr is not None:
                return attr
        raise KeyError(key)


class GetAtts:
    def __init__(self, regions: list[str]) -> None:
        self._regions = regions
        self._getatts: dict[str, _ResourceDict] = {}

        for region in self._regions:
            self._getatts[region] = _ResourceDict()

    def add(self, resource_name: str, resource: Resource) -> None:
        for region in self._regions:
            if resource_name not in self._getatts[region]:
                if resource.type.endswith("::MODULE"):
                    self._getatts[region][f"{resource_name}.*"] = (
                        PROVIDER_SCHEMA_MANAGER.get_type_getatts(
                            resource_type=resource.type, region=region
                        )
                    )

                try:
                    self._getatts[region][resource_name] = resource.get_atts(
                        region=region
                    )
                except ResourceNotFoundError:
                    self._getatts[region][resource_name] = AttributeDict()
                    continue

    def json_schema(self, region: str) -> dict:
        schema: dict[str, list[Any]] = {"oneOf": []}
        schema_strings: dict[str, Any] = {
            "type": "string",
            "enum": [],
        }
        schema_array: dict[str, str | list[Any]] = {
            "type": "array",
            "items": [{"type": "string", "enum": []}, {"type": ["string", "object"]}],
            "allOf": [],
        }

        for resource_name, attributes in self._getatts[region].items():
            attr_enum = []
            for attribute in attributes:
                attr_enum.append(attribute)
                schema_strings["enum"].append(
                    f"{resource_name}.{attribute}"
                )  # type: ignore

            schema_array["items"][0]["enum"].append(resource_name)  # type: ignore
            schema_array["allOf"].append(  # type: ignore
                {
                    "if": {
                        "items": [
                            {"type": "string", "const": resource_name},
                            {"type": ["string", "object"]},
                        ]
                    },
                    "then": {
                        "if": {
                            "items": [
                                {"type": "string", "const": resource_name},
                                {"type": "string"},
                            ]
                        },
                        "then": {
                            "items": [
                                {"type": "string", "const": resource_name},
                                {"type": "string", "enum": attr_enum},
                            ]
                        },
                        "else": {
                            "items": [
                                {"type": "string", "const": resource_name},
                                {
                                    "type": "object",
                                    "properties": {"Ref": {"type": "string"}},
                                    "required": ["Ref"],
                                    "additionalProperties": False,
                                },
                            ]
                        },
                    },
                    "else": {},
                }
            )

        schema["oneOf"].append(schema_array)
        schema["oneOf"].append(schema_strings)
        return schema

    def match(self, region: str, getatt: str | list[str]) -> str:
        if isinstance(getatt, str):
            getatt = getatt.split(".", 1)

        if isinstance(getatt, list):
            if len(getatt) != 2:
                raise TypeError("Invalid GetAtt size")

            try:
                result = (
                    self._getatts.get(region, _ResourceDict())
                    .get(getatt[0], AttributeDict())
                    .get(getatt[1])
                )
                if result is None:
                    raise ValueError("Attribute for resource doesn't exist")
                return result  # type: ignore
            except ValueError as e:
                raise e

        else:
            raise TypeError("Invalid GetAtt structure")
