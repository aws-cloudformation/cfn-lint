from collections import UserDict
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from cfnlint.helpers import RegexDict
from cfnlint.schema import (
    PROVIDER_SCHEMA_MANAGER,
    GetAtt,
    GetAttType,
    ResourceNotFoundError,
)


class _ResourceDict(UserDict):
    def __init__(self, __dict: None = None) -> None:
        self._has_modules: bool = False
        super().__init__(__dict)

    def __setitem__(self, key: str, item: Any) -> None:
        if key.endswith(".*"):
            self._has_modules = True
        return super().__setitem__(key, item)

    def __getitem__(self, key: str) -> Any:
        try:
            return super().__getitem__(key)
        except KeyError as e:
            if not self._has_modules:
                raise e
        l_key = ""  # longest key
        for k in self.data.keys():
            if not k.endswith(".*"):
                continue
            if key.startswith(k[:-2]):
                if len(k) > len(l_key):
                    l_key = k
        if l_key:
            return super().__getitem__(l_key)
        raise KeyError(key)


class GetAtts:
    # [region][resource_name][attribute][JsonSchema Dict]
    # Dict[str, RegexDict[str, RegexDict[str, GetAtt]]]
    _getatts: Dict[str, Dict[str, Dict[str, GetAtt]]]

    _astrik_string_types = ("AWS::CloudFormation::Stack",)
    _astrik_unknown_types = (
        "Custom::",
        "AWS::Serverless::",
        "AWS::CloudFormation::CustomResource",
    )

    def __init__(self, regions: List[str]) -> None:
        self._regions = regions
        self._getatts = {}
        for region in self._regions:
            self._getatts[region] = _ResourceDict()

    def add(self, resource_name: str, resource_type: str) -> None:
        for region in self._regions:
            if resource_name not in self._getatts[region]:
                if resource_type.endswith("::MODULE"):
                    self._getatts[region][f"{resource_name}.*"] = RegexDict()
                    self._getatts[region][resource_name][".*"] = GetAtt(
                        schema={}, getatt_type=GetAttType.ReadOnly
                    )
                    continue

                self._getatts[region][resource_name] = RegexDict()
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
        schema = {"oneOf": []}
        schema_strings = {
            "type": "string",
            "enum": [],
        }
        schema_array = {
            "type": "array",
            "items": [{"type": "string", "enum": []}, {"type": ["string", "object"]}],
            "allOf": [],
        }

        for resource_name, attributes in self._getatts[region].items():
            attr_enum = []
            for attribute in attributes:
                attr_enum.append(attribute)
                schema_strings["enum"].append(f"{resource_name}.{attribute}")

            schema_array["items"][0]["enum"].append(resource_name)
            schema_array["allOf"].append(
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
                result = self._getatts.get(region, {}).get(getatt[0], {}).get(getatt[1])
                if result is None:
                    raise ValueError("Attribute for resource doesn't exist")
                return result
            except ValueError as e:
                raise e

        else:
            raise TypeError("Invalid GetAtt structure")

    def items(self, region: Optional[str] = None) -> Iterable[Tuple[str, GetAtt]]:
        if region is None:
            region = self._regions[0]
            for k, v in self._getatts.get(region, {}).items():
                yield k, v
