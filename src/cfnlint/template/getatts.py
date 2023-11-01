from __future__ import annotations

from collections import UserDict
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import regex as re

from cfnlint.schema import (
    PROVIDER_SCHEMA_MANAGER,
    GetAtt,
    GetAttType,
    ResourceNotFoundError,
)


class _AttributeDict(UserDict):
    def __init__(self, __dict: None = None) -> None:
        super().__init__(__dict)
        self.data: Dict[str, GetAtt] = {}

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key: str) -> GetAtt:
        possible_items = {}
        for k, v in self.data.items():
            if re.fullmatch(k, key):
                possible_items[k] = v
        if not possible_items:
            raise KeyError(key)
        longest_match = sorted(possible_items.keys(), key=len)[-1]
        return possible_items[longest_match]


class _ResourceDict(UserDict):
    def __init__(self, __dict: None = None) -> None:
        self._has_modules: bool = False
        super().__init__(__dict)
        self.data: Dict[str, _AttributeDict] = {}

    def __setitem__(self, key: str, item: _AttributeDict) -> None:
        if key.endswith(".*"):
            self._has_modules = True
        return super().__setitem__(key, item)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key: str) -> _AttributeDict:
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
    def __init__(self, regions: List[str]) -> None:
        self._regions = regions
        self._getatts: Dict[str, _ResourceDict] = {}

        self._astrik_string_types = ("AWS::CloudFormation::Stack",)
        self._astrik_unknown_types = (
            "Custom::",
            "AWS::Serverless::",
            "AWS::CloudFormation::CustomResource",
        )
        for region in self._regions:
            self._getatts[region] = _ResourceDict()

    def add(self, resource_name: str, resource_type: str) -> None:
        for region in self._regions:
            if resource_name not in self._getatts[region]:
                if resource_type.endswith("::MODULE"):
                    self._getatts[region][f"{resource_name}.*"] = _AttributeDict()
                    self._getatts[region][resource_name][".*"] = GetAtt(
                        schema={}, getatt_type=GetAttType.ReadOnly
                    )
                    continue

                self._getatts[region][resource_name] = _AttributeDict()
                if resource_type.startswith(self._astrik_string_types):
                    self._getatts[region][resource_name]["Outputs\\..*"] = GetAtt(
                        schema={"type": "string"}, getatt_type=GetAttType.ReadOnly
                    )
                elif resource_type.startswith(self._astrik_unknown_types):
                    self._getatts[region][resource_name][".*"] = GetAtt(
                        schema={}, getatt_type=GetAttType.ReadOnly
                    )
                else:
                    try:
                        for (
                            attr_name,
                            attr_value,
                        ) in PROVIDER_SCHEMA_MANAGER.get_type_getatts(
                            resource_type=resource_type, region=region
                        ).items():
                            self._getatts[region][resource_name][attr_name] = attr_value
                    except ResourceNotFoundError:
                        continue

    def json_schema(self, region: str) -> Dict:
        schema: Dict[str, List] = {"oneOf": []}
        schema_strings: Dict[str, Any] = {
            "type": "string",
            "enum": [],
        }
        schema_array: Dict[str, Union[str, List]] = {
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

    def match(self, region: str, getatt: Union[str, List[str]]) -> GetAtt:
        if isinstance(getatt, str):
            getatt = getatt.split(".", 1)

        if isinstance(getatt, list):
            if len(getatt) != 2:
                raise TypeError("Invalid GetAtt size")

            try:
                result = (
                    self._getatts.get(region, _ResourceDict())
                    .get(getatt[0], _AttributeDict())
                    .get(getatt[1])
                )
                if result is None:
                    raise ValueError("Attribute for resource doesn't exist")
                return result  # type: ignore
            except ValueError as e:
                raise e

        else:
            raise TypeError("Invalid GetAtt structure")

    def items(
        self, region: Optional[str] = None
    ) -> Iterable[Tuple[str, _AttributeDict]]:
        if region is None:
            region = self._regions[0]
            for k, v in self._getatts.get(region, _ResourceDict()).items():
                yield k, v
