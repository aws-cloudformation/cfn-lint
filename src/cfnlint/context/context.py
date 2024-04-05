"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import InitVar, dataclass, field, fields
from typing import Any, Deque, Dict, Iterator, List, Mapping, Sequence, Set, Tuple

from cfnlint.helpers import PSEUDOPARAMS, REGION_PRIMARY
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, AttributeDict

_PSEUDOPARAMS_NON_REGION = ["AWS::AccountId", "AWS::NoValue", "AWS::StackName"]


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


@dataclass(frozen=True)
class Context:
    """
    A `Context` keeps track of the current context that we are evaluating against
    Arguments:

        region:

            The region being evaluated against.

        conditions:

            The conditions being used and their current state
    """

    # what regions we are processing
    regions: Sequence[str] = field(
        init=True, default_factory=lambda: list([REGION_PRIMARY])
    )

    # supported functions at this point in the template
    functions: Sequence[str] = field(init=True, default_factory=list)

    # path keeps track of the path as we move down the template
    # Example: Resources, MyResource, Properties, Name, ...
    path: Deque[str] = field(init=True, default_factory=deque)
    # value_path is an override of the value if we got it from another place
    # like a Parameter default value
    value_path: Deque[str] = field(init=True, default_factory=deque)

    # cfn-lint Template class
    parameters: Dict[str, "Parameter"] = field(init=True, default_factory=dict)
    resources: Dict[str, "Resource"] = field(init=True, default_factory=dict)
    conditions: Dict[str, "Condition"] = field(init=True, default_factory=dict)
    mappings: Dict[str, "Map"] = field(init=True, default_factory=dict)

    pseudo_parameters: Set[str] = field(
        init=True, default_factory=lambda: set(PSEUDOPARAMS)
    )

    # Combiniation of storing any resolved ref
    # and adds in any Refs available from things like Fn::Sub
    ref_values: Dict[str, Any] = field(init=True, default_factory=dict)

    # Resolved conditions for reference
    resolved_conditions: Mapping[str, bool] = field(init=True, default_factory=dict)

    transforms: Transforms = field(init=True, default_factory=lambda: Transforms([]))

    def __post_init__(self) -> None:
        if self.path is None:
            self.path = deque([])

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

    def ref_value(self, instance: str) -> Iterator[Tuple[str | List[str], "Context"]]:
        if instance in PSEUDOPARAMS and instance not in self.pseudo_parameters:
            return

        if instance in self.ref_values:
            yield self.ref_values[instance], self
            return

        # Non regionalized items first
        if instance in _PSEUDOPARAMS_NON_REGION and instance in self.pseudo_parameters:
            pseudo_value = _get_pseudo_value(instance)
            if pseudo_value is not None:
                yield pseudo_value, self.evolve(ref_values={instance: pseudo_value})
            return
        if instance in self.parameters:
            for v, path in self.parameters[instance].ref(self):
                yield v, self.evolve(
                    value_path=deque(["Parameters", instance]) + path,
                    ref_values={instance: v},
                )
            return

        # Regionalized values second
        if instance in PSEUDOPARAMS and instance in self.pseudo_parameters:
            for region in self.regions:
                # We can resolve all region based pseudo values
                # as we are now deciding on a region.
                yield _get_pseudo_value_by_region(instance, region), self.evolve(
                    regions=[region],
                    ref_values={
                        p: _get_pseudo_value_by_region(p, region)
                        for p in PSEUDOPARAMS
                        if p not in _PSEUDOPARAMS_NON_REGION
                    },
                )

    @property
    def refs(self):
        pseudo_params = list(self.pseudo_parameters)
        pseudo_params.sort()
        return (
            list(self.parameters.keys())
            + list(self.resources.keys())
            + pseudo_params
            + list(self.ref_values.keys())
        )


def _get_pseudo_value(parameter: str) -> str | List[str] | None:
    if parameter == "AWS::AccountId":
        return "123456789012"
    if parameter == "AWS::StackName":
        return "teststack"
    return None


def _get_pseudo_value_by_region(parameter: str, region: str) -> str | List[str]:
    if parameter == "AWS::NotificationARNs":
        return [f"arn:{_get_partition(region)}:sns:{region}:123456789012:notification"]
    if parameter == "AWS::Partition":
        return _get_partition(region)
    if parameter == "AWS::Region":
        return region
    if parameter == "AWS::StackId":
        return (
            f"arn:{_get_partition(region)}:cloudformation:{region}"
            ":123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"
        )
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
    def ref(self, context: Context) -> Iterator[Any]:
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
        self.default = None
        self.allowed_values = []
        self.min_value = None
        self.max_value = None

        t = parameter.get("Type")
        if not isinstance(t, str):
            raise ValueError("Type must be a string")
        self.type = t

        self.description = parameter.get("Description")

        # SSM Parameter defaults and allowed values point to
        # SSM paths not to the actual values
        if self.type.startswith("AWS::SSM::Parameter::"):
            return

        if self.type == "CommaDelimitedList" or self.type.startswith("List<"):
            if "Default" in parameter:
                self.default = parameter.get("Default").split(",")
            for allowed_value in parameter.get("AllowedValues", []):
                self.allowed_values.append(allowed_value.split(","))
        else:
            self.default = parameter.get("Default")
            self.allowed_values = parameter.get("AllowedValues")
            self.min_value = parameter.get("MinValue")
            self.max_value = parameter.get("MaxValue")

    def ref(self, context: Context) -> Iterator[Tuple[Any, deque]]:
        if self.allowed_values:
            for i, allowed_value in enumerate(self.allowed_values):
                yield allowed_value, deque(["AllowedValues", i])
            return
        # assume default is an allowed value so we skip it
        if self.default is not None:
            yield self.default, deque(["Default"])

        if self.min_value is not None:
            yield self.min_value, deque(["MinValue"])

        if self.max_value is not None:
            yield self.max_value, deque(["MaxValue"])


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

    def ref(self, context: Context) -> Iterator[Any]:
        return
        yield


@dataclass
class _MappingSecondaryKey:
    """
    This class holds a mapping value
    """

    keys: Dict[str, List[Any] | str | int | float] = field(
        init=False, default_factory=dict
    )
    instance: InitVar[Any]

    def __post_init__(self, instance) -> None:
        if not isinstance(instance, dict):
            raise ValueError("Secondary keys must be a object")
        for k, v in instance.items():
            if isinstance(v, (str, list, int, float)):
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

    def find_in_map(self, top_key: str, secondary_key: str) -> Iterator[Any]:
        if top_key not in self.keys:
            raise KeyError(top_key)
        yield self.keys[top_key].value(secondary_key)


def _init_parameters(parameters: Any) -> dict[str, Parameter]:
    obj = {}
    if not isinstance(parameters, dict):
        raise ValueError("Parameters must be a object")
    for k, v in parameters.items():
        try:
            obj[k] = Parameter(v)
        except ValueError:
            pass

    return obj


def _init_resources(resources: Any) -> dict[str, Resource]:
    obj = {}
    if not isinstance(resources, dict):
        raise ValueError("Resource must be a object")
    for k, v in resources.items():
        try:
            obj[k] = Resource(v)
        except ValueError:
            pass
    return obj


def _init_transforms(transforms: Any) -> Transforms:
    if isinstance(transforms, (str, list)):
        return Transforms(transforms)
    return Transforms([])


def _init_conditions(conditions: Any) -> dict[str, Condition]:
    obj = {}
    if not isinstance(conditions, dict):
        raise ValueError("Conditions must be a object")
    for k, v in conditions.items():
        try:
            obj[k] = Condition(v)
        except ValueError:
            pass

    return obj


def _init_mappings(mappings: Any) -> dict[str, Map]:
    obj = {}
    if not isinstance(mappings, dict):
        raise ValueError("Mappings must be a object")
    for k, v in mappings.items():
        try:
            obj[k] = Map(v)
        except ValueError:
            pass

    return obj


def create_context_for_template(cfn):
    parameters = {}
    try:
        parameters = _init_parameters(cfn.template.get("Parameters", {}))
    except (ValueError, AttributeError):
        pass

    resources = {}
    try:
        resources = _init_resources(cfn.template.get("Resources", {}))
    except (ValueError, AttributeError):
        pass

    transforms = _init_transforms(cfn.template.get("Transform", []))

    conditions = {}
    try:
        conditions = _init_conditions(cfn.template.get("Conditions", {}))
    except (ValueError, AttributeError):
        pass

    mappings = {}
    try:
        mappings = _init_mappings(cfn.template.get("Mappings", {}))
    except (ValueError, AttributeError):
        pass

    return Context(
        parameters=parameters,
        resources=resources,
        conditions=conditions,
        transforms=transforms,
        mappings=mappings,
        regions=cfn.regions,
        path=deque([]),
        functions=["Fn::Transform"],
    )
