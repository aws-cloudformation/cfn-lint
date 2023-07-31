"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from dataclasses import InitVar, dataclass, field, fields
from typing import Any, Deque, Dict, Sequence

from cfnlint.helpers import REGION_PRIMARY
from cfnlint.template import Template as CfnTemplate


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
    transforms: "Transforms" = field(init=True, default_factory=list)

    def evolve(self, **kwargs) -> "Context":
        """
        Create a new context merging together attributes
        """
        cls = self.__class__
        for f in fields(Context):
            if f.init:
                kwargs.setdefault(f.name, getattr(self, f.name))

        instance = cls(**kwargs)

        return instance


@dataclass
class Parameter:
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


@dataclass
class Resource:
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


@dataclass
class Transforms:
    # Template level parameters
    transforms: Sequence[str] = field(init=True, default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.transforms, list):
            self.transforms = [self.transforms]

        for transform in self.transforms:
            if not isinstance(transform, str):
                raise ValueError("Transform must be a string")

    def has_language_extensions_transform(self):
        lang_extensions_transform = "AWS::LanguageExtensions"
        return bool(lang_extensions_transform in self.transforms)


def _init_parameters(parameters: Any) -> None:
    results = {}
    if isinstance(parameters, dict):
        for k, v in parameters.items():
            try:
                results[k] = Parameter(v)
            except ValueError as e:
                pass
    return results


def _init_resources(resources: Any) -> None:
    results = {}
    if isinstance(resources, dict):
        for k, v in resources.items():
            try:
                results[k] = Parameter(v)
            except ValueError as e:
                pass
    return results


def _init_transforms(transforms: Any) -> None:
    if isinstance(transforms, (str, list)):
        return Transforms(transforms)
    return Transforms([])


def create_context_for_resource_properties(cfn: CfnTemplate, region: str) -> Context:
    """
    Create a context for a resource properties
    """
    parameters = _init_parameters(cfn.template.get("Parameters", {}))
    resources = _init_resources(cfn.template.get("Resources", {}))
    transforms = _init_transforms(cfn.template.get("Transform", []))

    return Context(
        parameters=parameters, resources=resources, transforms=transforms, region=region
    )


def create_context_for_outputs(cfn: CfnTemplate, region: str) -> Context:
    """
    Create a context for a resource properties
    """
    parameters = _init_parameters(cfn.template.get("Parameters", {}))
    resources = _init_resources(cfn.template.get("Resources", {}))
    transforms = _init_transforms(cfn.template.get("Transform", []))

    return Context(
        parameters=parameters, resources=resources, transforms=transforms, region=region
    )
