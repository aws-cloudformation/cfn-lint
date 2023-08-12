"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import InitVar, dataclass, field, fields
from typing import Any, Deque, Dict, Iterable, List, Sequence

from cfnlint.helpers import FUNCTIONS, PSEUDOPARAMS, REGION_PRIMARY
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, AttributeDict
from cfnlint.template import Template as CfnTemplate


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
    conditions: Dict[str, bool] = field(init=True, default_factory=dict)

    # path keeps track of the path as we move down the template
    # Example: Resources, MyResource, Properties, Name, ...
    path: Deque[str] = field(init=True, default_factory=deque)

    # The path of the value we are currently processing
    # Example: When using a Ref this could be to default parameter value
    value_path: Deque[str] = field(init=True, default_factory=deque)

    # cfn-lint Template class
    parameters: Dict[str, "Parameter"] = field(init=True, default_factory=dict)
    resources: Dict[str, "Resource"] = field(init=True, default_factory=dict)
    ref_values: Dict[str, Any] = field(init=True, default_factory=dict)

    transforms: Transforms = field(init=True, default=Transforms([]))

    def __post_init__(self) -> None:
        if self.transforms is None:
            self.transforms = _init_transforms([])
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

    def fn_value(self, instance: Dict[str, Any]) -> Any:
        """
        Return the value of a ref
        """
        if len(instance) != 1:
            raise ValueError(
                "Fn::Value can only have one key, got: %s" % list(instance.keys())
            )
        for k, v in instance.items():
            if k == "Ref":
                return self.ref_value(v)
            if k == "Fn::FindInMap":
                return self.fn_find_in_map(v)
            raise ValueError(f"Unsupported value {v!r}")


def _get_pseudo_value(parameter, region) -> str:
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
    if parameter == "AWS::URLSuffix":
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
    def ref(self) -> Iterable[Any]:
        pass


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
    region: str = field(init=True)

    def __post_init__(self, resource) -> None:
        t = resource.get("Type")
        if not isinstance(t, str):
            raise ValueError("Type must be a string")
        self.type = t

    @property
    def get_atts(self) -> AttributeDict:
        return PROVIDER_SCHEMA_MANAGER.get_type_getatts(self.type, self.region)

    def ref(self, context: Context) -> Iterable[Any]:
        return
        yield


def _init_parameters(parameters: Any) -> Dict[str, Parameter]:
    results = {}
    if isinstance(parameters, dict):
        for k, v in parameters.items():
            try:
                results[k] = Parameter(v)
            except ValueError:
                pass
    return results


def _init_resources(resources: Any, region: str) -> Dict[str, Resource]:
    results = {}
    if isinstance(resources, dict):
        for k, v in resources.items():
            try:
                if k.startswith("Fn::ForEach::"):
                    results[k] = Resource(v[2], region)
                else:
                    results[k] = Resource(v, region)
            except ValueError:
                pass
    return results


def _init_transforms(transforms: Any) -> "Transforms":
    if isinstance(transforms, (str, list)):
        return Transforms(transforms)
    return Transforms([])


def create_context_for_resources(cfn: CfnTemplate, region: str) -> Context:
    """
    Create a context for a resources
    """
    parameters = _init_parameters(cfn.template.get("Parameters", {}))
    resources = _init_resources(cfn.template.get("Resources", {}), region)
    transforms = _init_transforms(cfn.template.get("Transform", []))

    functions = []
    if transforms.has_language_extensions_transform():
        functions = ["Fn::ForEach::[a-zA-Z0-9]+"]

    return Context(
        parameters=parameters,
        resources=resources,
        transforms=transforms,
        region=region,
        path=deque(["Resources"]),
        functions=functions,
    )


def create_context_for_resource_properties(
    cfn: CfnTemplate, region: str, resource_name: str
) -> Context:
    """
    Create a context for a resource properties
    """
    parameters = _init_parameters(cfn.template.get("Parameters", {}))
    resources = _init_resources(cfn.template.get("Resources", {}), region)
    transforms = _init_transforms(cfn.template.get("Transform", []))

    return Context(
        parameters=parameters,
        resources=resources,
        transforms=transforms,
        region=region,
        path=deque(["Resources", resource_name, "Properties"]),
        functions=list(FUNCTIONS),
    )


def create_context_for_outputs(cfn: CfnTemplate, region: str) -> Context:
    """
    Create a context for a resource properties
    """
    parameters = _init_parameters(cfn.template.get("Parameters", {}))
    resources = _init_resources(cfn.template.get("Resources", {}), region)
    transforms = _init_transforms(cfn.template.get("Transform", []))

    return Context(
        parameters=parameters,
        resources=resources,
        transforms=transforms,
        region=region,
        path=deque(["Outputs"]),
        functions=["Fn::ForEach"],
    )
