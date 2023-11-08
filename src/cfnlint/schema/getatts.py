"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import enum
from collections import UserDict
from typing import Any, Dict, Optional

import regex as re

from cfnlint.schema._pointer import resolve_pointer

_all_property_types = [
    "AWS::Amplify::Branch",
    "AWS::AppMesh::GatewayRoute",
    "AWS::AppMesh::Mesh",
    "AWS::AppMesh::Route",
    "AWS::AppMesh::VirtualGateway",
    "AWS::AppMesh::VirtualNode",
    "AWS::AppMesh::VirtualRouter",
    "AWS::AppMesh::VirtualService",
    "AWS::AppSync::DataSource",
    "AWS::AppSync::Resolver",
    "AWS::Backup::BackupSelection",
    "AWS::Backup::BackupVault",
    "AWS::CloudWatch::InsightRule",
    "AWS::EC2::CapacityReservation",
    "AWS::EC2::Instance",
    "AWS::EC2::SecurityGroup",
    "AWS::EC2::Subnet",
    "AWS::EC2::VPC",
    "AWS::EFS::MountTarget",
    "AWS::EKS::Nodegroup",
    "AWS::Events::EventBus",
    "AWS::EventSchemas::Discoverer",
    "AWS::EventSchemas::Registry",
    "AWS::EventSchemas::Schema",
    "AWS::GameLift::GameSessionQueue",
    "AWS::GameLift::MatchmakingConfiguration",
    "AWS::GameLift::MatchmakingRuleSet",
    "AWS::IoT1Click::Placement",
    "AWS::IoT1Click::Project",
    "AWS::Kinesis::StreamConsumer",
    "AWS::MediaConvert::JobTemplate",
    "AWS::MediaConvert::Preset",
    "AWS::MediaConvert::Queue",
    "AWS::OpsWorks::Instance",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::SageMaker::CodeRepository",
    "AWS::SageMaker::Endpoint",
    "AWS::SageMaker::EndpointConfig",
    "AWS::SageMaker::Model",
    "AWS::SageMaker::NotebookInstance",
    "AWS::SageMaker::NotebookInstanceLifecycleConfig",
    "AWS::SageMaker::Workteam",
    "AWS::ServiceDiscovery::Service",
    "AWS::SNS::Topic",
    "AWS::SQS::Queue",
    "AWS::StepFunctions::Activity",
    "AWS::Transfer::User",
    "AWS::Amplify::Domain",
    "AWS::AppSync::FunctionConfiguration",
    "AWS::Cloud9::EnvironmentEC2",
    "AWS::DocDB::DBCluster",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::Greengrass::ConnectorDefinition",
    "AWS::Greengrass::CoreDefinition",
    "AWS::Greengrass::DeviceDefinition",
    "AWS::Greengrass::FunctionDefinition",
    "AWS::Greengrass::Group",
    "AWS::Greengrass::LoggerDefinition",
    "AWS::Greengrass::ResourceDefinition",
    "AWS::Greengrass::SubscriptionDefinition",
    "AWS::IoT1Click::Device",
    "AWS::ManagedBlockchain::Member",
    "AWS::ManagedBlockchain::Node",
    "AWS::MediaLive::Input",
    "AWS::Neptune::DBCluster",
    "AWS::OpsWorks::UserProfile",
    "AWS::RoboMaker::RobotApplication",
    "AWS::RoboMaker::SimulationApplication",
    "AWS::Route53Resolver::ResolverEndpoint",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::SSM::Parameter",
    "AWS::CodeArtifact::Domain",
    "AWS::CodeArtifact::Repository",
    "AWS::SageMaker::DataQualityJobDefinition",
    "AWS::SageMaker::ModelQualityJobDefinition",
    "AWS::SageMaker::ModelBiasJobDefinition",
    "AWS::SageMaker::ModelExplainabilityJobDefinition",
    "AWS::SageMaker::MonitoringSchedule",
    "AWS::ImageBuilder::Component",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::RDS::DBParameterGroup",
    "AWS::AppSync::DomainName",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::S3::AccessPoint",
    "AWS::Grafana::Workspace",
    "AWS::RDS::DBInstance",
]

_unnamed_string_types = ("AWS::CloudFormation::Stack",)

_unnamed_unknown_types = (
    "Custom::",
    "AWS::Serverless::",
    "AWS::CloudFormation::CustomResource",
)


class AttributeDict(UserDict):
    def __init__(self, __dict: None = None) -> None:
        super().__init__(__dict)
        self.data: Dict[str, GetAtt] = {}

    def __getitem__(self, key: str) -> "GetAtt":
        possible_items = {}
        for k, v in self.data.items():
            if re.fullmatch(k, key):
                possible_items[k] = v
        if not possible_items:
            raise KeyError(key)
        longest_match = sorted(possible_items.keys(), key=len)[-1]
        return possible_items[longest_match]

    def __repr__(self) -> str:
        keys = []
        for k in self.data.keys():
            keys.append(k.replace("\\", ""))
        return f"{keys!r}"


class GetAttType(enum.Enum):
    ReadOnly = 1
    All = 2
    Unnamed = 3


class GetAtt:
    def __init__(self, schema: Dict[str, Any], getatt_type: GetAttType) -> None:
        self._getatt_type: GetAttType = getatt_type
        self._type: Optional[str] = schema.get("type")
        self._item_type: Optional[str]
        if self._type == "array":
            self._item_type = schema.get("items", {}).get("type")

    @property
    def type(self) -> Optional[str]:
        return self._type

    @property
    def item_type(self) -> Optional[str]:
        return self._item_type

    @property
    def getatt_type(self) -> GetAttType:
        return self._getatt_type


class GetAtts:
    """Class for helping with GetAtt logic"""

    _attrs: AttributeDict = AttributeDict()
    _schema: Dict[str, Any] = {}

    def __init__(self, schema: Dict[str, Any]) -> None:
        self._attrs = AttributeDict()
        self._schema = schema
        type_name = schema.get("typeName", "")
        if type_name in _all_property_types:
            for name, value in schema.get("properties", {}).items():
                self._process_schema(name, value, GetAttType.All)
            return
        for unnamed_type in _unnamed_string_types:
            if type_name.startswith(unnamed_type):
                self._attrs["Outputs\\..*"] = GetAtt(
                    schema={"type": "string"}, getatt_type=GetAttType.Unnamed
                )
        for unnamed_type in _unnamed_unknown_types:
            if type_name.startswith(unnamed_type):
                self._attrs[".*"] = GetAtt(
                    schema={
                        "type": [
                            "string",
                            "number",
                            "boolean",
                            "object",
                            "array",
                            "integer",
                        ]
                    },
                    getatt_type=GetAttType.Unnamed,
                )
        for ro_attr in schema.get("readOnlyProperties", []):
            try:
                name = ".".join(ro_attr.split("/")[2:])
                ro_schema = self._flatten_schema_by_pointer(ro_attr)
                self._process_schema(name, ro_schema, GetAttType.ReadOnly)
            except KeyError:
                pass

    def _flatten_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        r_schema = schema.copy()
        for k, v in schema.items():
            if k == "$ref":
                r_schema.pop(k)
                r_schema = {**r_schema, **self._flatten_schema_by_pointer(v)}
            elif k == "items":
                r_schema[k] = self._flatten_schema(v)
        return r_schema

    def _flatten_schema_by_pointer(self, ptr: str) -> Dict[str, Any]:
        schema = resolve_pointer(self._schema, ptr)
        return self._flatten_schema(schema)

    def _process_schema(
        self, name: str, schema: Dict[str, Any], getatt_type: GetAttType
    ):
        if schema.get("type") == "object":
            for prop, value in schema.get("properties", {}).items():
                self._process_schema(f"{name}.{prop}", value, getatt_type)
        elif schema.get("type") == "array":
            # GetAtt doesn't support going into an array of objects or another array
            # so we only look at an array of strings, etc.
            self._attrs[name] = GetAtt(schema, getatt_type)
        else:
            self._attrs[name] = GetAtt(schema, getatt_type)

    @property
    def attrs(self) -> AttributeDict:
        return self._attrs
