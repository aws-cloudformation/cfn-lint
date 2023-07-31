"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Sequence

from cfnlint.template import Template as CfnTemplate


@dataclass
class Template:
    """
    This class allows working with template level attributes
    easier by only storing valid parameters, resources, etc.

    We only validate the basic structure of these items not the values.
    Thats what our rules are for.
    """

    cfn: InitVar[CfnTemplate]
    parameters: Dict[str, "Parameter"] = field(init=False, default_factory=dict)
    resources: Dict[str, "Resource"] = field(init=False, default_factory=dict)
    transforms: "Transforms" = field(init=False, default_factory=list)

    def __post_init__(self, cfn: CfnTemplate) -> None:
        self._init_parameters(cfn.template.get("Parameters", {}))
        self._init_resources(cfn.template.get("Resources", {}))
        self._init_transforms(cfn.template.get("Transforms", []))

    def _init_parameters(self, parameters: Any) -> None:
        if isinstance(parameters, dict):
            for k, v in parameters.items():
                try:
                    self.parameters[k] = Parameter(v)
                except ValueError as e:
                    pass

    def _init_resources(self, resources: Any) -> None:
        if isinstance(resources, dict):
            for k, v in resources.items():
                try:
                    self.resources[k] = Parameter(v)
                except ValueError as e:
                    pass

    def _init_transforms(self, transforms: Any) -> None:
        if isinstance(transforms, list):
            self.transforms = Transforms(transforms)
