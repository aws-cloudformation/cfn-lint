"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import UserDict
from typing import TYPE_CHECKING, Any

import regex as re

from cfnlint.helpers import ensure_list

if TYPE_CHECKING:
    from cfnlint.schema import Schema


_all_property_types = [
    "AWS::Amplify::Branch",
    "AWS::Amplify::Domain",
    "AWS::AppSync::DomainName",
    "AWS::AppSync::FunctionConfiguration",
    "AWS::AppSync::Resolver",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::Backup::BackupSelection",
    "AWS::Backup::BackupVault",
    "AWS::CodeArtifact::Domain",
    "AWS::CodeArtifact::Repository",
    "AWS::EC2::CapacityReservation",
    "AWS::EC2::Instance",
    "AWS::EC2::SecurityGroup",
    "AWS::EC2::Subnet",
    "AWS::EC2::VPC",
    "AWS::EFS::MountTarget",
    "AWS::EKS::Nodegroup",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::Events::EventBus",
    "AWS::EventSchemas::Discoverer",
    "AWS::EventSchemas::Registry",
    "AWS::EventSchemas::Schema",
    "AWS::GameLift::GameSessionQueue",
    "AWS::GameLift::MatchmakingConfiguration",
    "AWS::GameLift::MatchmakingRuleSet",
    "AWS::Grafana::Workspace",
    "AWS::Greengrass::ConnectorDefinition",
    "AWS::Greengrass::CoreDefinition",
    "AWS::Greengrass::DeviceDefinition",
    "AWS::Greengrass::FunctionDefinition",
    "AWS::Greengrass::Group",
    "AWS::Greengrass::LoggerDefinition",
    "AWS::Greengrass::ResourceDefinition",
    "AWS::Greengrass::SubscriptionDefinition",
    "AWS::ImageBuilder::Component",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::Neptune::DBCluster",
    "AWS::RDS::DBInstance",
    "AWS::RDS::DBParameterGroup",
    "AWS::RoboMaker::RobotApplication",
    "AWS::RoboMaker::SimulationApplication",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::S3::AccessPoint",
    "AWS::SageMaker::DataQualityJobDefinition",
    "AWS::SageMaker::ModelBiasJobDefinition",
    "AWS::SageMaker::ModelExplainabilityJobDefinition",
    "AWS::SageMaker::ModelQualityJobDefinition",
    "AWS::SageMaker::MonitoringSchedule",
    "AWS::SNS::Topic",
    "AWS::SQS::Queue",
    "AWS::SSM::Parameter",
    "AWS::StepFunctions::Activity",
]

# Non registry resources that have a difference between readOnlyProperties
# what is supported by GetAtt
_exceptions = {
    "AWS::AppMesh::GatewayRoute": [
        "GatewayRouteName",
        "MeshName",
        "MeshOwner",
        "VirtualGatewayName",
    ],
    "AWS::AppMesh::Mesh": [
        "MeshName",
    ],
    "AWS::AppMesh::Route": [
        "MeshName",
        "MeshOwner",
        "RouteName",
        "VirtualRouterName",
    ],
    "AWS::AppMesh::VirtualGateway": [
        "MeshName",
        "MeshOwner",
        "VirtualGatewayName",
    ],
    "AWS::AppMesh::VirtualNode": [
        "MeshName",
        "MeshOwner",
        "VirtualNodeName",
    ],
    "AWS::AppMesh::VirtualRouter": [
        "MeshName",
        "MeshOwner",
        "VirtualRouterName",
    ],
    "AWS::AppMesh::VirtualService": [
        "MeshName",
        "MeshOwner",
        "VirtualServiceName",
    ],
    "AWS::AppSync::DataSource": [
        "Name",
    ],
    "AWS::Cloud9::EnvironmentEC2": [
        "Name",
    ],
    "AWS::CloudWatch::InsightRule": [
        "RuleName",
    ],
    "AWS::DocDB::DBCluster": [
        "Port",
    ],
    "AWS::EC2::Instance": [
        "AvailabilityZone",
    ],
    "AWS::EC2::SecurityGroup": ["VpcId"],
    "AWS::Greengrass::ConnectorDefinition": [
        "Name",
    ],
    "AWS::Greengrass::CoreDefinition": [
        "Name",
    ],
    "AWS::Greengrass::DeviceDefinition": [
        "Name",
    ],
    "AWS::Greengrass::FunctionDefinition": [
        "Name",
    ],
    "AWS::Greengrass::Group": [
        "Name",
        "RoleArn",
    ],
    "AWS::Greengrass::LoggerDefinition": [
        "Name",
    ],
    "AWS::Greengrass::ResourceDefinition": [
        "Name",
    ],
    "AWS::Greengrass::SubscriptionDefinition": [
        "Name",
    ],
    "AWS::IoT1Click::Device": [
        "Enabled",
    ],
    "AWS::IoT1Click::Placement": [
        "PlacementName",
        "ProjectName",
    ],
    "AWS::IoT1Click::Project": [
        "ProjectName",
    ],
    "AWS::Kinesis::StreamConsumer": [
        "ConsumerName",
        "StreamARN",
    ],
    "AWS::ManagedBlockchain::Member": [
        "NetworkId",
    ],
    "AWS::MediaConvert::JobTemplate": [
        "Name",
    ],
    "AWS::MediaConvert::Preset": [
        "Name",
    ],
    "AWS::MediaConvert::Queue": [
        "Name",
    ],
    "AWS::MediaLive::Input": [
        "Destinations",
        "Sources",
    ],
    "AWS::OpsWorks::Instance": ["AvailabilityZone"],
    "AWS::OpsWorks::UserProfile": ["SshUsername"],
    "AWS::Route53Resolver::ResolverEndpoint": [
        "Direction",
        "Name",
    ],
    "AWS::SageMaker::CodeRepository": ["CodeRepositoryName"],
    "AWS::SageMaker::Endpoint": [
        "EndpointName",
    ],
    "AWS::SageMaker::EndpointConfig": ["EndpointConfigName"],
    "AWS::SageMaker::Model": ["ModelName"],
    "AWS::SageMaker::NotebookInstance": ["NotebookInstanceName"],
    "AWS::SageMaker::NotebookInstanceLifecycleConfig": [
        "NotebookInstanceLifecycleConfigName"
    ],
    "AWS::SageMaker::Workteam": ["WorkteamName"],
    "AWS::ServiceDiscovery::Service": ["Name"],
    "AWS::Transfer::User": [
        "ServerId",
        "UserName",
    ],
}

_unnamed_unknown_types = (
    "Custom::",
    "AWS::Serverless::",
    "AWS::CloudFormation::CustomResource",
    "Module",
)


class AttributeDict(UserDict):
    def __init__(self, __dict: None = None) -> None:
        super().__init__(__dict)
        self.data: dict[str, str] = {}

    def __getitem__(self, key: str) -> str:
        possible_items = {}
        for k, v in self.data.items():
            if re.fullmatch(k, key) or k == key:
                possible_items[k] = v
        if not possible_items:
            raise KeyError(key)
        longest_match = sorted(possible_items.keys(), key=len)[-1]
        return possible_items[longest_match]

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __repr__(self) -> str:
        keys = []
        for k in self.data.keys():
            keys.append(k.replace("\\", ""))
        return f"{keys!r}"


class GetAtts:
    """Class for helping with GetAtt logic"""

    def __init__(self, schema: "Schema") -> None:
        self._attrs = AttributeDict()
        if schema.type_name in _all_property_types:
            for name, value in schema.schema.get("properties", {}).items():
                self._process_schema(value, schema, f"/properties/{name}")
            return
        if schema.type_name in _exceptions:
            for name in _exceptions[schema.type_name]:
                self._attrs[self._pointer_to_attr(f"/properties/{name}")] = (
                    f"/properties/{name}"
                )

        if schema.type_name == "AWS::CloudFormation::Stack":
            self._attrs["Outputs\\..*"] = "/properties/CfnLintStringType"
            return

        if schema.type_name == "AWS::ServiceCatalog::CloudFormationProvisionedProduct":
            for ro_attr in schema.schema.get("readOnlyProperties", []):
                if ro_attr == "/properties/Outputs":
                    self._attrs["Outputs\\..*"] = "/properties/CfnLintStringType"
                else:
                    self._attrs[self._pointer_to_attr(ro_attr)] = ro_attr
            return

        for unnamed_type in _unnamed_unknown_types:
            if schema.type_name.startswith(unnamed_type):
                self._attrs[".*"] = "/properties/CfnLintAllTypes"

        for ro_attr in schema.schema.get("readOnlyProperties", []):
            self._attrs[self._pointer_to_attr(ro_attr)] = ro_attr

    def _pointer_to_attr(self, pointer: str) -> str:
        return ".".join(pointer.split("/")[2:])

    def _process_schema(self, obj: dict[str, Any], schema: "Schema", path: str):
        types = ensure_list(obj.get("type"))
        if "object" in types:
            for prop, value in obj.get("properties", {}).items():
                self._process_schema(value, schema, f"{path}/{prop}")
        elif "array" in types:
            # GetAtt doesn't support going into an array of objects or another array
            # so we only look at an array of strings, etc.
            if obj.get("items", {}).get("type") in ["object", "array"]:
                return
            self._attrs[self._pointer_to_attr(path)] = path
        elif obj.get("$ref"):
            _, obj = schema.resolver.resolve(obj.get("$ref"))
            self._process_schema(obj, schema, path)
        else:
            self._attrs[self._pointer_to_attr(path)] = path

    @property
    def attrs(self) -> AttributeDict:
        return self._attrs
