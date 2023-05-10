"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import enum
from typing import Any, Dict, Optional

from cfnlint.schema._pointer import resolve_pointer

_all_property_types = [
    "AWS::Amplify::Branch",
    "AWS::Amplify::Domain",
    "AWS::AppSync::DomainName",
    "AWS::Backup::BackupSelection",
    "AWS::Backup::BackupVault",
    "AWS::CodeArtifact::Domain",
    "AWS::CodeArtifact::Repository",
    "AWS::EC2::CapacityReservation",
    "AWS::EC2::Subnet",
    "AWS::EC2::VPC",
    "AWS::EFS::MountTarget",
    "AWS::EKS::Nodegroup",
    "AWS::ImageBuilder::Component",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::RDS::DBParameterGroup",
    "AWS::RoboMaker::RobotApplication",
    "AWS::RoboMaker::SimulationApplication",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::SNS::Topic",
    "AWS::SQS::Queue",
    "AWS::SageMaker::DataQualityJobDefinition",
    "AWS::SageMaker::ModelBiasJobDefinition",
    "AWS::SageMaker::ModelExplainabilityJobDefinition",
    "AWS::SageMaker::ModelQualityJobDefinition",
    "AWS::SageMaker::MonitoringSchedule",
    "AWS::StepFunctions::Activity",
]


class GetAttType(enum.Enum):
    ReadOnly = 1
    All = 2


class GetAtt:
    def __init__(self, schema: Dict[str, Any], getatt_type: GetAttType) -> None:
        self._getatt_type: GetAttType = getatt_type
        self._type: str = schema.get("type")
        self._item_type: Optional[str]
        if self._type == "array":
            self._item_type: Optional[str] = schema.get("items", {}).get("type")

    @property
    def type(self) -> str:
        return self._type

    @property
    def item_type(self) -> Optional[str]:
        return self._item_type

    @property
    def getatt_type(self) -> GetAttType:
        return self._getatt_type


class GetAtts:
    """Class for helping with GetAtt logic"""

    _attrs: Dict[str, GetAtt] = {}
    _schema = {}

    def __init__(self, schema: Dict[str, Any]) -> None:
        self._attrs = {}
        self._schema = schema
        type_name = schema.get("typeName", "")
        if type_name in _all_property_types:
            for name, value in schema.get("properties", {}).items():
                self._process_schema(name, value, GetAttType.All)
            return
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
    def attrs(self) -> Dict[str, GetAtt]:
        return self._attrs
