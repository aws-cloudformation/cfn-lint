"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import InitVar, dataclass, field, fields
from typing import Any, Deque, Dict, Iterable, List, Mapping, Sequence

from cfnlint.helpers import FUNCTIONS, PSEUDOPARAMS, REGION_PRIMARY
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, AttributeDict


@dataclass
class Transforms:
    # Template level parameters
    transforms: InitVar[str | List[str] | None]
    _transforms: List[str] = field(init=False, default_factory=list)

    def __post_init__(self, transforms) -> None:
        if transforms is None:
            return
        if not isinstance(transforms, list):
            transforms = [transforms]

        for transform in transforms:
            if not isinstance(transform, str):
                raise ValueError("Transform must be a string")
            self._transforms.append(transform)

    def has_language_extensions_transform(self):
        lang_extensions_transform = "AWS::LanguageExtensions"
        return bool(lang_extensions_transform in self._transforms)


@dataclass
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
    region: str = field(init=True, default=REGION_PRIMARY)

    functions: Sequence[str] = field(init=True, default_factory=list)
    # As we move down the template this is used to keep track of the
    # how the conditions affected the path we are on
    # The key is the condition name and the value is if the condition
    # was true or false

    # path keeps track of the path as we move down the template
    # Example: Resources, MyResource, Properties, Name, ...
    path: Deque[str] = field(init=True, default_factory=deque)
    value_path: Deque[str] = field(init=True, default_factory=deque)

    # cfn-lint Template class
    parameters: Dict[str, "Parameter"] = field(init=True, default_factory=dict)
    resources: Dict[str, "Resource"] = field(init=True, default_factory=dict)
    conditions: Dict[str, "Condition"] = field(init=True, default_factory=dict)
    mappings: Dict[str, "Map"] = field(init=True, default_factory=dict)

    # other Refs from Fn::Sub
    ref_values: Dict[str, Any] = field(init=True, default_factory=dict)

    # Resolved value
    resolved_conditions: Mapping[str, bool] = field(init=True, default_factory=dict)

    transforms: Transforms = field(init=True, default_factory=lambda: Transforms([]))

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = deque([])
        for pseudo_parameter in PSEUDOPARAMS:
            self.ref_values[pseudo_parameter] = _get_pseudo_value(
                pseudo_parameter, self.region
            )

    def evolve(self, **kwargs) -> "Context":
        """
        Create a new context merging together attributes
        """
        cls = self.__class__

        if "path" in kwargs and kwargs["path"] is not None:
            path = self.path.copy()
            path.append(kwargs["path"])
            kwargs["path"] = path
        else:
            kwargs["path"] = self.path.copy()

        if "ref_values" in kwargs and kwargs["ref_values"] is not None:
            ref_values = self.ref_values.copy()
            ref_values.update(kwargs["ref_values"])
            kwargs["ref_values"] = ref_values

        for f in fields(Context):
            if f.init:
                kwargs.setdefault(f.name, getattr(self, f.name))

        return cls(**kwargs)

    @property
    def refs(self):
        return (
            list(self.parameters.keys())
            + list(self.resources.keys())
            + list(self.ref_values.keys())
        )


def _get_pseudo_value(parameter: str, region: str) -> str | List[str] | None:
    if parameter == "AWS::AccountId":
        return "123456789012"
    if parameter == "AWS::NotificationARNs":
        return [f"arn:{_get_partition(region)}:sns:{region}:123456789012:notification"]
    if parameter == "AWS::NoValue":
        return None
    if parameter == "AWS::Partition":
        return _get_partition(region)
    if parameter == "AWS::Region":
        return region
    if parameter == "AWS::StackId":
        return (
            f"arn:{_get_partition(region)}:cloudformation:{region}"
            ":123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"
        )
    if parameter == "AWS::StackName":
        return "teststack"
    # if parameter == "AWS::URLSuffix":
    if region in ("cn-north-1", "cn-northwest-1"):
        return "amazonaws.com.cn"
    else:
        return "amazonaws.com"


def _get_partition(region) -> str:
    if region in ("us-gov-east-1", "us-gov-west-1"):
        return "aws-us-gov"
    if region in ("cn-north-1", "cn-northwest-1"):
        return "aws-cn"
    else:
        return "aws"


class _Ref(ABC):
    """
    Abstract class for all ref types
    """

    @abstractmethod
    def ref(self, context: Context) -> Iterable[Any]:
        pass


@dataclass
class Condition:
    instance: Any = field(init=True)


@dataclass
class Parameter(_Ref):
    """
    This class holds a parameter and its attributes
    """

    type: str = field(init=False)
    default: Any = field(init=False)
    allowed_values: Any = field(init=False)
    description: str = field(init=False)

    parameter: InitVar[Any]

    def __post_init__(self, parameter) -> None:
        t = parameter.get("Type")
        if not isinstance(t, str):
            raise ValueError("Type must be a string")
        self.type = t

        self.default = parameter.get("Default")
        self.allowed_values = parameter.get("AllowedValues")
        self.description = parameter.get("Description")

    def ref(self, context: Context) -> Iterable[Any]:
        if self.default:
            yield self.default
        if self.allowed_values:
            for allowed_value in self.allowed_values:
                yield allowed_value


@dataclass
class Resource(_Ref):
    """
    This class holds a resources and its type
    """

    type: str = field(init=False)
    resource: InitVar[Any]

    def __post_init__(self, resource) -> None:
        t = resource.get("Type")
        if not isinstance(t, str):
            raise ValueError("Type must be a string")
        self.type = t

    @property
    def get_atts(self, region: str = "us-east-1") -> AttributeDict:
        return PROVIDER_SCHEMA_MANAGER.get_type_getatts(self.type, region)

    def ref(self, context: Context) -> Iterable[Any]:
        return
        yield


@dataclass
class _MappingSecondaryKey:
    """
    This class holds a mapping value
    """

    keys: Dict[str, List[Any] | str] = field(init=False, default_factory=dict)
    instance: InitVar[Any]

    def __post_init__(self, instance) -> None:
        if not isinstance(instance, dict):
            raise ValueError("Secondary keys must be a object")
        for k, v in instance.items():
            if isinstance(v, (str, list)):
                self.keys[k] = v

    def value(self, secondary_key: str):
        if secondary_key not in self.keys:
            raise KeyError(secondary_key)
        return self.keys[secondary_key]


@dataclass
class Map:
    """
    This class holds a mapping
    """

    keys: Dict[str, _MappingSecondaryKey] = field(init=False, default_factory=dict)
    resource: InitVar[Any]

    def __post_init__(self, mapping) -> None:
        if not isinstance(mapping, dict):
            raise ValueError("Mapping must be a object")
        for k, v in mapping.items():
            self.keys[k] = _MappingSecondaryKey(v)

    def find_in_map(self, top_key: str, secondary_key: str) -> Iterable[Any]:
        if top_key not in self.keys:
            raise KeyError(top_key)
        yield self.keys[top_key].value(secondary_key)


@dataclass
class ContextManager:
    cfn: InitVar[Any]
    parameters: Dict[str, Parameter] = field(init=False)
    resources: Dict[str, Resource] = field(init=False)
    transforms: Transforms = field(init=False)
    conditions: Dict[str, Condition] = field(init=False)
    mappings: Dict[str, Map] = field(init=False)

    def __post_init__(self, cfn: Any) -> None:
        self.parameters = {}
        self.resources = {}
        self.conditions = {}
        self.mappings = {}
        try:
            self._init_parameters(cfn.template.get("Parameters", {}))
        except (ValueError, AttributeError):
            pass
        try:
            self._init_resources(cfn.template.get("Resources", {}))
        except (ValueError, AttributeError):
            pass
        self._init_transforms(cfn.template.get("Transform", []))
        try:
            self._init_conditions(cfn.template.get("Conditions", {}))
        except (ValueError, AttributeError):
            pass
        try:
            self._init_mappings(cfn.template.get("Mappings", {}))
        except (ValueError, AttributeError):
            pass

    def _init_parameters(self, parameters: Any) -> None:
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a object")
        for k, v in parameters.items():
            self.parameters[k] = Parameter(v)

    def _init_resources(self, resources: Any) -> None:
        if not isinstance(resources, dict):
            raise ValueError("Resource must be a object")
        for k, v in resources.items():
            self.resources[k] = Resource(v)

    def _init_transforms(self, transforms: Any) -> None:
        if isinstance(transforms, (str, list)):
            self.transforms = Transforms(transforms)
            return
        self.transforms = Transforms([])

    def _init_conditions(self, conditions: Any) -> None:
        if not isinstance(conditions, dict):
            raise ValueError("Conditions must be a object")
        for k, v in conditions.items():
            self.conditions[k] = Condition(v)

    def _init_mappings(self, mappings: Any) -> None:
        if not isinstance(mappings, dict):
            raise ValueError("Mappings must be a object")
        for k, v in mappings.items():
            self.mappings[k] = Map(v)

    collection: Dict | List[str | Dict] = field(init=False)
    output: Dict[str, Any] = field(init=False)

    def create_context_for_resources(self, region: str) -> Context:
        """
        Create a context for a resources
        """
        return Context(
            parameters=self.parameters,
            resources=self.resources,
            conditions=self.conditions,
            transforms=self.transforms,
            mappings=self.mappings,
            region=region,
            path=deque(["Resources"]),
            functions=[],
        )

    def create_context_for_resource_properties(
        self, region: str, resource_name: str
    ) -> Context:
        """
        Create a context for a resource properties
        """

        return Context(
            parameters=self.parameters,
            resources=self.resources,
            conditions=self.conditions,
            transforms=self.transforms,
            mappings=self.mappings,
            region=region,
            path=deque(["Resources", resource_name, "Properties"]),
            functions=list(FUNCTIONS),
        )

    def create_context_for_outputs(self, region: str) -> Context:
        """
        Create a context for a resource properties
        """

        return Context(
            parameters=self.parameters,
            resources=self.resources,
            conditions=self.conditions,
            transforms=self.transforms,
            mappings=self.mappings,
            region=region,
            path=deque(["Outputs"]),
            functions=[],
        )

    def create_context_for_conditions(self, region: str) -> Context:
        """
        Create a context for a conditions
        """

        return Context(
            parameters=self.parameters,
            resources={},
            conditions=self.conditions,
            mappings=self.mappings,
            transforms=self.transforms,
            region=region,
            path=deque(["Conditions"]),
            functions=[],
        )
