"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections import deque
from copy import deepcopy
from dataclasses import InitVar, dataclass, field, fields
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Deque, Iterator, Set, Tuple

import regex as re

from cfnlint.context._mappings import Mappings
from cfnlint.context.conditions._conditions import Conditions
from cfnlint.context.parameters import ParameterSet
from cfnlint.helpers import (
    BOOLEAN_STRINGS_TRUE,
    FUNCTIONS,
    PSEUDOPARAMS,
    REGEX_DYN_REF,
    REGION_PRIMARY,
    TRANSFORM_LANGUAGE_EXTENSION,
    TRANSFORM_SAM,
)
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, AttributeDict

if TYPE_CHECKING:
    from cfnlint.template import Template

_PSEUDOPARAMS_NON_REGION = ["AWS::AccountId", "AWS::NoValue", "AWS::StackName"]


@dataclass
class Transforms:
    # Template level parameters
    obj: InitVar[str | list[str] | None]
    _transforms: list[str] = field(init=False, default_factory=list)

    def __post_init__(self, obj) -> None:
        if obj is None:
            return
        if not isinstance(obj, list):
            obj = [obj]

        for transform in obj:
            if not isinstance(transform, str):
                continue
            self._transforms.append(transform)

        self.has_sam_transform = lru_cache()(self.has_sam_transform)  # type: ignore
        self.has_language_extensions_transform = lru_cache()(  # type: ignore
            self.has_language_extensions_transform
        )

    @property
    def transforms(self):
        return self._transforms

    def has_language_extensions_transform(self):
        return bool(TRANSFORM_LANGUAGE_EXTENSION in self._transforms)

    def has_sam_transform(self):
        # this function will always return False as SAM transform
        # will eliminate itself when the transform is done
        return bool(TRANSFORM_SAM in self._transforms)


@dataclass(frozen=True)
class Path:
    """
    A `Path` keeps track of the different Path values
    """

    # path keeps track of the path as we move down the template
    # Example: Resources, MyResource, Properties, Name, ...
    path: Deque[str | int] = field(init=True, default_factory=deque)

    # value_path is an override of the value if we got it from another place
    # like a Parameter default value
    # Example: Parameters, MyParameter, Default, ...
    value_path: Deque[str | int] = field(init=True, default_factory=deque)

    # cfn_path is a generic path used by cfn-lint to help make
    # writing rules easier.  The resource name is replaced by the type
    # lists are replaced with a *
    # Example: Resources, AWS::S3::Bucket, Properties, Name, ...
    # Example: Resources, *, Type
    cfn_path: Deque[str] = field(init=True, default_factory=deque)

    def descend(self, **kwargs) -> "Path":
        """
        Create a new Path by appending values
        """
        cls = self.__class__

        if kwargs.get("cfn_path") in FUNCTIONS:
            raise ValueError(f"{kwargs['cfn_path']!r} cannot be in 'cfn_path'")
        elif isinstance(kwargs.get("cfn_path"), int):
            raise ValueError(f"{kwargs['cfn_path']!r} cannot be an integer")

        for f in fields(Path):
            if kwargs.get(f.name) is not None:
                kwargs[f.name] = getattr(self, f.name) + deque([kwargs[f.name]])
            else:
                kwargs[f.name] = getattr(self, f.name)

        return cls(**kwargs)

    def evolve(self, **kwargs):
        """
        Create a new path without appending values
        """
        cls = self.__class__

        for f in fields(Path):
            kwargs.setdefault(f.name, getattr(self, f.name))

        return cls(**kwargs)

    @property
    def path_string(self):
        return "/".join(str(p) for p in self.path)

    @property
    def cfn_path_string(self):
        return "/".join(self.cfn_path)


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
    regions: list[str] = field(
        init=True, default_factory=lambda: list([REGION_PRIMARY])
    )

    # supported functions at this point in the template
    functions: list[str] = field(init=True, default_factory=list)

    path: Path = field(init=True, default_factory=Path)

    # cfn-lint Template class
    parameters: dict[str, "Parameter"] = field(init=True, default_factory=dict)
    resources: dict[str, "Resource"] = field(init=True, default_factory=dict)
    conditions: Conditions = field(init=True, default_factory=Conditions)
    mappings: Mappings = field(init=True, default_factory=Mappings)

    strict_types: bool = field(init=True, default=True)

    # When True, function validators should return unknown errors
    # instead of validating. Used in composite validators
    # (if/then/else, oneOf, anyOf) to handle unresolvable functions
    unresolvable_function_mode: bool = field(init=True, default=False)

    pseudo_parameters: Set[str] = field(
        init=True, default_factory=lambda: set(PSEUDOPARAMS)
    )

    # Combination of storing any resolved ref
    # and adds in any Refs available from things like Fn::Sub
    ref_values: dict[str, Any] = field(init=True, default_factory=dict)

    transforms: Transforms = field(init=True, default_factory=lambda: Transforms([]))

    # is the value a resolved value
    is_resolved_value: bool = field(init=True, default=False)
    resolve_pseudo_parameters: bool = field(init=True, default=True)

    # Deployment parameters
    parameter_sets: list[ParameterSet] | None = field(init=True, default_factory=list)
    is_resolved_from_parameters: bool = field(init=True, default=False)

    # For rule exceptions.  This is primarily used for if/then/else statements in which
    # exceptions will affect the results.
    allow_exceptions: bool = field(init=True, default=True)

    # Cached: logical IDs of MODULE-type resources
    module_names: tuple[str, ...] = field(init=False, default=())

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "module_names",
            tuple(
                name
                for name, resource in self.resources.items()
                if resource.type.endswith("::MODULE")
                or resource.type.startswith("AWS::Serverless::")
            ),
        )

    def evolve(self, **kwargs) -> "Context":
        """
        Create a new context without merging together attributes
        """
        cls = self.__class__

        if "ref_values" in kwargs:
            new_ref_values = self.ref_values.copy()
            new_ref_values.update(kwargs["ref_values"])
            kwargs["ref_values"] = new_ref_values

        for f in fields(Context):
            if f.init:
                kwargs.setdefault(f.name, getattr(self, f.name))

        return cls(**kwargs)

    def ref_value(self, instance: str) -> Iterator[Tuple[str | list[str], "Context"]]:
        if instance in PSEUDOPARAMS:
            if not self.resolve_pseudo_parameters:
                return
            if instance not in self.pseudo_parameters:
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

        # Regionalized values second
        if instance in PSEUDOPARAMS and instance in self.pseudo_parameters:
            for region in self.regions:
                # We can resolve all region based pseudo values
                # as we are now deciding on a region.
                yield (
                    _get_pseudo_value_by_region(instance, region),
                    self.evolve(
                        regions=[region],
                        ref_values={
                            p: _get_pseudo_value_by_region(p, region)
                            for p in PSEUDOPARAMS
                            if p not in _PSEUDOPARAMS_NON_REGION
                        },
                    ),
                )

        if instance in self.parameters:
            # if parameter sets are configured we use those first
            # we default to the parameter values if the parameter isn't in that set
            if self.parameter_sets is not None and len(self.parameter_sets) > 0:
                for parameter_set in self.parameter_sets:
                    if instance in parameter_set.parameters:
                        yield (
                            parameter_set.parameters[instance],
                            self.evolve(
                                ref_values=parameter_set.parameters,
                                parameter_sets=None,
                                is_resolved_from_parameters=True,
                            ),
                        )
                    else:
                        for v, path in self.parameters[instance].default_value():
                            parameters = deepcopy(parameter_set.parameters)
                            parameters.update({instance: v})
                            yield (
                                v,
                                self.evolve(
                                    path=self.path.evolve(
                                        value_path=deque(["Parameters", instance])
                                        + path
                                    ),
                                    ref_values=parameters,
                                    parameter_sets=None,
                                    is_resolved_from_parameters=True,
                                ),
                            )
                return

            for v, path in self.parameters[instance].ref_value(self):
                # validate that ref is possible with path
                # need to evaluate if Fn::If would be not true if value is
                # what it is
                yield (
                    v,
                    self.evolve(
                        path=self.path.evolve(
                            value_path=deque(["Parameters", instance]) + path
                        ),
                        ref_values={instance: v},
                        is_resolved_from_parameters=True,
                    ),
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


def _get_pseudo_value(parameter: str) -> str | list[str] | None:
    if parameter == "AWS::AccountId":
        return "123456789012"
    if parameter == "AWS::StackName":
        return "teststack"
    return None


def _get_pseudo_value_by_region(parameter: str, region: str) -> str | list[str]:
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
    def ref(self, region: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def ref_value(self, context: Context) -> Iterator[Tuple[Any, deque]]:
        pass


def _strip(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


@dataclass
class Parameter(_Ref):
    """
    This class holds a parameter and its attributes
    """

    type: str = field(init=False)
    default: Any = field(init=False)
    allowed_values: Any = field(init=False)
    description: str | None = field(init=False)
    ssm_path: str | None = field(init=False, default=None)

    parameter: InitVar[Any]

    def __post_init__(self, parameter) -> None:
        if not isinstance(parameter, dict):
            raise ValueError("Parameter must be a object")

        self.is_ssm_parameter = lru_cache()(self.is_ssm_parameter)  # type: ignore

        self.default = None
        self.allowed_values = []
        self.min_value = None
        self.max_value = None
        self.no_echo = False

        t = parameter.get("Type")
        if not isinstance(t, str):
            raise ValueError("Type must be a string")
        self.type = t

        self.description = parameter.get("Description")

        # SSM Parameter defaults and allowed values point to
        # SSM paths not to the actual values
        if self.is_ssm_parameter():
            self.ssm_path = parameter.get("Default", "")
            return

        if self.type == "CommaDelimitedList" or self.type.startswith("List<"):
            if "Default" in parameter:
                default = parameter.get("Default", "")
                if isinstance(default, str):
                    self.default = [_strip(value) for value in default.split(",")]
                else:
                    self.default = [_strip(default)]

            for allowed_value in parameter.get("AllowedValues", []):
                if isinstance(allowed_value, str):
                    self.allowed_values.append(
                        [_strip(value) for value in allowed_value.split(",")]
                    )
                else:
                    self.allowed_values.append([_strip(allowed_value)])
        else:
            self.default = parameter.get("Default")
            self.allowed_values = parameter.get("AllowedValues")

        self.min_value = parameter.get("MinValue")
        self.max_value = parameter.get("MaxValue")
        if parameter.get("NoEcho") in list(BOOLEAN_STRINGS_TRUE) + [True]:
            self.no_echo = True

    def ref(self, region: str = REGION_PRIMARY) -> dict[str, Any]:
        return {}

    def default_value(self) -> Iterator[Tuple[str | list[str], deque]]:
        if self.default is not None:
            if isinstance(self.default, list):
                yield [str(x) for x in self.default], deque(["Default"])
            else:
                yield str(self.default), deque(["Default"])

    def ref_value(self, context: Context) -> Iterator[Tuple[Any, deque]]:
        if self.allowed_values:
            for i, allowed_value in enumerate(self.allowed_values):
                if isinstance(allowed_value, list):
                    yield [str(x) for x in allowed_value], deque(["AllowedValues", i])
                else:
                    yield str(allowed_value), deque(["AllowedValues", i])
            # assume default is an allowed value so we skip it
            return

        yield from self.default_value()

        if self.min_value is not None:
            yield str(self.min_value), deque(["MinValue"])

        if self.max_value is not None:
            yield str(self.max_value), deque(["MaxValue"])

    def is_ssm_parameter(self) -> bool:
        return self.type.startswith("AWS::SSM::Parameter::")


def _nested_stack_get_atts(filename: str, template_url: str) -> None | AttributeDict:
    if (
        template_url.startswith("http://")
        or template_url.startswith("https://")
        or template_url.startswith("s3://")
    ):
        return None

    base_dir = os.path.dirname(os.path.abspath(filename))
    template_path = os.path.normpath(os.path.join(base_dir, template_url))

    if re.match(REGEX_DYN_REF, template_path):
        return None
    try:
        from cfnlint.decode import decode

        (tmp, matches) = decode(template_path)
    except Exception:  # noqa: E722
        return None
    if matches or tmp is None:
        return None

    outputs = AttributeDict()

    tmp_outputs = tmp.get("Outputs")
    if not isinstance(tmp_outputs, dict):
        return outputs

    for name, _ in tmp_outputs.items():
        outputs[f"Outputs.{name}"] = "/properties/CfnLintStringType"
    return outputs


@dataclass
class Resource(_Ref):
    """
    This class holds a resources and its type
    """

    type: str = field(init=False)
    condition: str | None = field(init=False, default=None)
    resource: InitVar[Any]
    filename: InitVar[str | None] = field(default=None)
    _nested_stack_get_atts: AttributeDict | None = field(init=False, default=None)

    def __post_init__(self, resource: Any, filename: str | None) -> None:
        if not isinstance(resource, dict):
            raise ValueError("Resource must be a object")
        t = resource.get("Type")
        if not isinstance(t, str):
            raise ValueError("Type must be a string")
        self.type = t
        if self.type.startswith("Custom::"):
            self.type = "AWS::CloudFormation::CustomResource"

        c = resource.get("Condition")
        if not isinstance(t, str):
            raise ValueError("Condition must be a string")
        self.condition = c

        if filename is None:
            return

        if self.type == "AWS::CloudFormation::Stack":
            properties = resource.get("Properties")
            if isinstance(properties, dict):
                template_url = properties.get("TemplateURL")
                if isinstance(template_url, str):
                    self._nested_stack_get_atts = _nested_stack_get_atts(
                        filename, template_url
                    )

    def get_atts(self, region: str = REGION_PRIMARY) -> AttributeDict:
        if self._nested_stack_get_atts is not None:
            return self._nested_stack_get_atts
        return PROVIDER_SCHEMA_MANAGER.get_type_getatts(self.type, region)

    def ref(self, region: str = REGION_PRIMARY) -> dict[str, Any]:
        return PROVIDER_SCHEMA_MANAGER.get_type_ref(self.type, region)

    def ref_value(self, context: Context) -> Iterator[Tuple[Any, deque]]:
        return
        yield


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


def _init_resources(resources: Any, filename: str | None = None) -> dict[str, Resource]:
    obj = {}
    if not isinstance(resources, dict):
        raise ValueError("Resource must be a object")
    for k, v in resources.items():
        try:
            obj[k] = Resource(v, filename)
        except ValueError:
            pass
    return obj


def _init_transforms(transforms: Any) -> Transforms:
    if isinstance(transforms, (str, list)):
        return Transforms(transforms)
    return Transforms([])


def _inject(
    resources: dict[str, Resource], logical_id: str, resource_type: str
) -> None:
    """Add a synthetic resource if it doesn't already exist."""
    if logical_id not in resources:
        try:
            resources[logical_id] = Resource({"Type": resource_type})
        except ValueError:
            pass


def _inject_sam_implicit_resources(
    template_resources: Any, resources: dict[str, Resource]
) -> None:
    """Add synthetic resources for SAM implicit APIs and generated roles.

    SAM auto-generates these when Functions have Api/HttpApi events
    without explicit RestApiId/ApiId references, and IAM Roles when
    no explicit Role property is set.
    """
    if not isinstance(template_resources, dict):
        return

    needs_rest_api = False
    needs_http_api = False

    for resource_id, resource in template_resources.items():
        if not isinstance(resource, dict):
            continue
        resource_type = resource.get("Type")
        props = resource.get("Properties", {})
        if not isinstance(props, dict):
            props = {}

        # SAM Functions/StateMachines without explicit Role get a generated Role
        if resource_type in (
            "AWS::Serverless::Function",
            "AWS::Serverless::StateMachine",
        ):
            if "Role" not in props:
                _inject(resources, f"{resource_id}Role", "AWS::IAM::Role")

        if resource_type == "AWS::Serverless::Function":
            # Version/Alias when AutoPublishAlias or DeploymentPreference
            has_alias = "AutoPublishAlias" in props or "DeploymentPreference" in props
            if has_alias:
                for suffix, rtype in (
                    (f"{resource_id}.Version", "AWS::Lambda::Version"),
                    (f"{resource_id}.Alias", "AWS::Lambda::Alias"),
                ):
                    if suffix not in resources:
                        try:
                            resources[suffix] = Resource({"Type": rtype})
                        except ValueError:
                            pass

            # Url when FunctionUrlConfig is set
            if "FunctionUrlConfig" in props:
                _inject(resources, f"{resource_id}Url", "AWS::Lambda::Url")

            # DeploymentPreference generates CodeDeploy resources
            dp = props.get("DeploymentPreference", {})
            if isinstance(dp, dict) and dp.get("Enabled", True):
                _inject(
                    resources,
                    "ServerlessDeploymentApplication",
                    "AWS::CodeDeploy::Application",
                )
                _inject(
                    resources,
                    f"{resource_id}DeploymentGroup",
                    "AWS::CodeDeploy::DeploymentGroup",
                )
                if "Role" not in dp:
                    _inject(resources, "CodeDeployServiceRole", "AWS::IAM::Role")

            # Per-event permissions and implicit API detection
            events = props.get("Events", {})
            if isinstance(events, dict):
                for event_name, event in events.items():
                    if not isinstance(event, dict):
                        continue
                    _inject(
                        resources,
                        f"{resource_id}{event_name}Permission",
                        "AWS::Lambda::Permission",
                    )
                    event_type = event.get("Type")
                    if event_type == "Api":
                        event_props = event.get("Properties", {})
                        if (
                            not isinstance(event_props, dict)
                            or "RestApiId" not in event_props
                        ):
                            needs_rest_api = True
                    elif event_type == "HttpApi":
                        event_props = event.get("Properties", {})
                        if (
                            not isinstance(event_props, dict)
                            or "ApiId" not in event_props
                        ):
                            needs_http_api = True

        if resource_type == "AWS::Serverless::Api":
            _inject(resources, f"{resource_id}Stage", "AWS::ApiGateway::Stage")
            if "Domain" in props:
                _inject(
                    resources,
                    f"{resource_id}DomainName",
                    "AWS::ApiGateway::DomainName",
                )
            if "Auth" in props:
                _inject(
                    resources,
                    f"{resource_id}UsagePlan",
                    "AWS::ApiGateway::UsagePlan",
                )

        if resource_type == "AWS::Serverless::HttpApi":
            _inject(resources, f"{resource_id}Stage", "AWS::ApiGatewayV2::Stage")

    if needs_rest_api:
        _inject(resources, "ServerlessRestApi", "AWS::Serverless::Api")
        _inject(resources, "ServerlessRestApiStage", "AWS::ApiGateway::Stage")

    if needs_http_api:
        _inject(resources, "ServerlessHttpApi", "AWS::Serverless::HttpApi")
        _inject(resources, "ServerlessHttpApiStage", "AWS::ApiGatewayV2::Stage")


def create_context_for_template(
    cfn: Template,
) -> "Context":
    parameters = {}
    try:
        parameters = _init_parameters(cfn.template.get("Parameters", {}))
    except (ValueError, AttributeError):
        pass

    resources = {}
    try:
        resources = _init_resources(cfn.template.get("Resources", {}), cfn.filename)
    except (ValueError, AttributeError):
        pass

    # Inject synthetic resources for SAM implicit APIs.
    # When a SAM Function has an Api event without an explicit RestApiId,
    # SAM generates "ServerlessRestApi" (AWS::Serverless::Api).
    # Similarly for HttpApi events -> "ServerlessHttpApi".
    if cfn.has_serverless_transform():
        _inject_sam_implicit_resources(cfn.template.get("Resources", {}), resources)

    transforms = _init_transforms(cfn.template.get("Transform", []))

    try:
        conditions = Conditions.create_from_instance(
            cfn.template.get("Conditions", {}),
            cfn.template.get("Rules", {}),
            parameters,
        )
    except (ValueError, AttributeError):
        conditions = Conditions.create_from_instance({}, {}, {})

    mappings = Mappings.create_from_dict(cfn.template.get("Mappings", {}))

    return Context(
        parameters=parameters,
        resources=resources,
        conditions=conditions,
        transforms=transforms,
        mappings=mappings,
        regions=cfn.regions,
        path=Path(),
        functions=["Fn::Transform"],
        ref_values={},
        parameter_sets=[],
    )
