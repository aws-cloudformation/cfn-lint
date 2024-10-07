#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import logging
import os
from collections import namedtuple
from typing import List

LOGGER = logging.getLogger("cfnlint")

Patch = namedtuple("Patch", ["values", "path"])
ResourcePatch = namedtuple("ResourcePatch", ["resource_type", "patches"])
patches: List[ResourcePatch] = []


common_patches = {
    "BlockDeviceMapping": {
        "requiredXor": ["VirtualName", "Ebs", "NoDevice"],
    },
}

patches.extend(
    [
        ResourcePatch(
            resource_type="AWS::ApiGateway::Stage",
            patches=[
                Patch(
                    path="/definitions/MethodSetting/properties/ResourcePath",
                    values={
                        "pattern": r"^/.*$",
                    },
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ApplicationAutoScaling::ScalingPolicy",
            patches=[
                Patch(
                    path="/",
                    values={
                        "requiredXor": ["ScalingTargetId", "ResourceId"],
                        "dependentRequired": {
                            "ResourceId": ["ScalableDimension", "ServiceNamespace"],
                        },
                    },
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AppStream::Fleet",
            patches=[
                Patch(
                    values={"maximum": 360000, "minimum": 60},
                    path="/properties/DisconnectTimeoutInSeconds",
                ),
                Patch(
                    values={"maximum": 3600, "minimum": 0},
                    path="/properties/IdleDisconnectTimeoutInSeconds",
                ),
                Patch(
                    values={"maximum": 360000, "minimum": 600},
                    path="/properties/MaxUserDurationInSeconds",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScaling::AutoScalingGroup",
            patches=[
                Patch(
                    values={"enum": ["EC2", "ELB"]},
                    path="/properties/HealthCheckType",
                ),
                Patch(
                    values={"requiredXor": ["LaunchTemplateId", "LaunchTemplateName"]},
                    path="/definitions/LaunchTemplateSpecification",
                ),
                Patch(
                    values={
                        "requiredXor": [
                            "InstanceId",
                            "LaunchConfigurationName",
                            "LaunchTemplate",
                            "MixedInstancesPolicy",
                        ]
                    },
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScaling::LaunchConfiguration",
            patches=[
                Patch(
                    values=common_patches.get("BlockDeviceMapping"),
                    path="/definitions/BlockDeviceMapping",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScaling::LifecycleHook",
            patches=[
                Patch(
                    values={"enum": ["ABANDON", "CONTINUE"]},
                    path="/properties/DefaultResult",
                ),
                Patch(
                    values={
                        "enum": [
                            "autoscaling:EC2_INSTANCE_LAUNCHING",
                            "autoscaling:EC2_INSTANCE_TERMINATING",
                        ]
                    },
                    path="/properties/LifecycleTransition",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScaling::ScalingPolicy",
            patches=[
                Patch(
                    values={
                        "enum": [
                            "ChangeInCapacity",
                            "ExactCapacity",
                            "PercentChangeInCapacity",
                        ]
                    },
                    path="/properties/AdjustmentType",
                ),
                Patch(
                    values={"enum": ["Average", "Maximum", "Minimum"]},
                    path="/properties/MetricAggregationType",
                ),
                Patch(
                    values={
                        "enum": [
                            "PredictiveScaling",
                            "SimpleScaling",
                            "StepScaling",
                            "TargetTrackingScaling",
                        ]
                    },
                    path="/properties/PolicyType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Budgets::Budget",
            patches=[
                Patch(
                    values={
                        "maximum": 1000000000,
                        "minimum": 0.1,
                    },
                    path="/definitions/Notification/properties/Threshold",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudFormation::WaitCondition",
            patches=[
                Patch(
                    values={"maximum": 43200, "minimum": 0},
                    path="/properties/Timeout",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudFront::Distribution",
            patches=[
                Patch(
                    path="/definitions/ViewerCertificate",
                    values={
                        "requiredXor": [
                            "AcmCertificateArn",
                            "CloudFrontDefaultCertificate",
                            "IamCertificateId",
                        ]
                    },
                ),
                Patch(
                    path="/definitions/Origin",
                    values={
                        "dependentExcluded": {
                            "CustomOriginConfig": ["S3OriginConfig"],
                            "S3OriginConfig": ["CustomOriginConfig"],
                        }
                    },
                ),
                Patch(
                    path="/definitions/CustomErrorResponse",
                    values={
                        "dependentRequired": {"ResponseCode": ["ResponsePagePath"]}
                    },
                ),
                Patch(
                    path="/definitions/ViewerCertificate",
                    values={
                        "dependentRequired": {
                            "AcmCertificateArn": ["SslSupportMethod"],
                            "IamCertificateId": ["SslSupportMethod"],
                        }
                    },
                ),
                Patch(
                    values={
                        "enum": [400, 403, 404, 405, 414, 416, 500, 501, 502, 503, 504]
                    },
                    path="/definitions/CustomErrorResponse/properties/ErrorCode",
                ),
                Patch(
                    values={
                        "enum": [
                            200,
                            400,
                            403,
                            404,
                            405,
                            414,
                            416,
                            500,
                            501,
                            502,
                            503,
                            504,
                        ]
                    },
                    path="/definitions/CustomErrorResponse/properties/ResponseCode",
                ),
                Patch(
                    values={
                        "enum": [
                            "AD",
                            "AE",
                            "AF",
                            "AG",
                            "AI",
                            "AL",
                            "AM",
                            "AO",
                            "AQ",
                            "AR",
                            "AS",
                            "AT",
                            "AU",
                            "AW",
                            "AX",
                            "AZ",
                            "BA",
                            "BB",
                            "BD",
                            "BE",
                            "BF",
                            "BG",
                            "BH",
                            "BI",
                            "BJ",
                            "BL",
                            "BM",
                            "BN",
                            "BO",
                            "BQ",
                            "BR",
                            "BS",
                            "BT",
                            "BV",
                            "BW",
                            "BY",
                            "BZ",
                            "CA",
                            "CC",
                            "CD",
                            "CF",
                            "CG",
                            "CH",
                            "CI",
                            "CK",
                            "CL",
                            "CM",
                            "CN",
                            "CO",
                            "CR",
                            "CU",
                            "CV",
                            "CW",
                            "CX",
                            "CY",
                            "CZ",
                            "DE",
                            "DJ",
                            "DK",
                            "DM",
                            "DO",
                            "DZ",
                            "EC",
                            "EE",
                            "EG",
                            "EH",
                            "ER",
                            "ES",
                            "ET",
                            "FI",
                            "FJ",
                            "FK",
                            "FM",
                            "FO",
                            "FR",
                            "GA",
                            "GB",
                            "GD",
                            "GE",
                            "GF",
                            "GG",
                            "GH",
                            "GI",
                            "GL",
                            "GM",
                            "GN",
                            "GP",
                            "GQ",
                            "GR",
                            "GS",
                            "GT",
                            "GU",
                            "GW",
                            "GY",
                            "HK",
                            "HM",
                            "HN",
                            "HR",
                            "HT",
                            "HU",
                            "ID",
                            "IE",
                            "IL",
                            "IM",
                            "IN",
                            "IO",
                            "IQ",
                            "IR",
                            "IS",
                            "IT",
                            "JE",
                            "JM",
                            "JO",
                            "JP",
                            "KE",
                            "KG",
                            "KH",
                            "KI",
                            "KM",
                            "KN",
                            "KP",
                            "KR",
                            "KW",
                            "KY",
                            "KZ",
                            "LA",
                            "LB",
                            "LC",
                            "LI",
                            "LK",
                            "LR",
                            "LS",
                            "LT",
                            "LU",
                            "LV",
                            "LY",
                            "MA",
                            "MC",
                            "MD",
                            "ME",
                            "MF",
                            "MG",
                            "MH",
                            "MK",
                            "ML",
                            "MM",
                            "MN",
                            "MO",
                            "MP",
                            "MQ",
                            "MR",
                            "MS",
                            "MT",
                            "MU",
                            "MV",
                            "MW",
                            "MX",
                            "MY",
                            "MZ",
                            "NA",
                            "NC",
                            "NE",
                            "NF",
                            "NG",
                            "NI",
                            "NL",
                            "NO",
                            "NP",
                            "NR",
                            "NU",
                            "NZ",
                            "OM",
                            "PA",
                            "PE",
                            "PF",
                            "PG",
                            "PH",
                            "PK",
                            "PL",
                            "PM",
                            "PN",
                            "PR",
                            "PS",
                            "PT",
                            "PW",
                            "PY",
                            "QA",
                            "RE",
                            "RO",
                            "RS",
                            "RU",
                            "RW",
                            "SA",
                            "SB",
                            "SC",
                            "SD",
                            "SE",
                            "SG",
                            "SH",
                            "SI",
                            "SJ",
                            "SK",
                            "SL",
                            "SM",
                            "SN",
                            "SO",
                            "SR",
                            "SS",
                            "ST",
                            "SV",
                            "SX",
                            "SY",
                            "SZ",
                            "TC",
                            "TD",
                            "TF",
                            "TG",
                            "TH",
                            "TJ",
                            "TK",
                            "TL",
                            "TM",
                            "TN",
                            "TO",
                            "TR",
                            "TT",
                            "TV",
                            "TW",
                            "TZ",
                            "UA",
                            "UG",
                            "UM",
                            "US",
                            "UY",
                            "UZ",
                            "VA",
                            "VC",
                            "VE",
                            "VG",
                            "VI",
                            "VN",
                            "VU",
                            "WF",
                            "WS",
                            "YE",
                            "YT",
                            "ZA",
                            "ZM",
                            "ZW",
                        ]
                    },
                    path="/definitions/GeoRestriction/properties/Locations/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudTrail::Trail",
            patches=[
                Patch(
                    values={
                        "enum": [
                            "AWS::Lambda::Function",
                            "AWS::S3::Object",
                            "AWS::DynamoDB::Table",
                            "AWS::S3Outposts::Object",
                            "AWS::ManagedBlockchain::Node",
                            "AWS::S3ObjectLambda::AccessPoint",
                            "AWS::EC2::Snapshot",
                            "AWS::S3::AccessPoint",
                            "AWS::DynamoDB::Stream",
                        ]
                    },
                    path="/definitions/DataResource/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudWatch::Alarm",
            patches=[
                Patch(
                    values={
                        "requiredXor": ["Metrics", "MetricName"],
                        "dependentExcluded": {
                            "Metrics": [
                                "MetricName",
                                "Dimensions",
                                "Period",
                                "Namespace",
                                "Statistic",
                                "ExtendedStatistic",
                                "Unit",
                            ],
                            "Statistic": ["ExtendedStatistic"],
                            "ExtendedStatistic": ["Statistic"],
                            "Threshold": ["ThresholdMetricId"],
                            "ThresholdMetricId": ["Threshold"],
                        },
                    },
                    path="/",
                ),
                Patch(
                    values={"maximum": 1024, "minimum": 1},
                    path="/properties/AlarmActions/items",
                ),
                Patch(
                    values={"maxItems": 5, "minItems": 0},
                    path="/properties/AlarmActions",
                ),
                Patch(
                    values={"pattern": "^([a-z])([A-Za-z0-9\\_]*)$"},
                    path="/definitions/MetricDataQuery/properties/Id",
                ),
                Patch(
                    values={"enum": ["breaching", "ignore", "missing", "notBreaching"]},
                    path="/properties/TreatMissingData",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeBuild::Project",
            patches=[
                Patch(
                    values={"maximum": 480, "minimum": 5},
                    path="/properties/QueuedTimeoutInMinutes",
                ),
                Patch(
                    values={"maximum": 480, "minimum": 5},
                    path="/properties/TimeoutInMinutes",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                Patch(
                    values={
                        "maximum": 100,
                        "minimum": 1,
                        "pattern": "^[a-zA-Z0-9._\\-]+(?<!\\.git)$",
                    },
                    path="/properties/RepositoryName",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodePipeline::Pipeline",
            patches=[
                Patch(
                    values={"requiredXor": ["ArtifactStore", "ArtifactStores"]},
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Config::ConfigRule",
            patches=[
                Patch(
                    values={"maxLength": 256, "minLength": 1},
                    path="/properties/Description",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DocDB::DBCluster",
            patches=[
                Patch(
                    values={"enum": ["3.6.0", "4.0", "4.0.0", "5.0.0"]},
                    path="/properties/EngineVersion",
                ),
                Patch(
                    values={"maximum": 35, "minimum": 1},
                    path="/properties/BackupRetentionPeriod",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DynamoDB::Table",
            patches=[
                Patch(
                    values={
                        "allOf": [
                            {
                                "if": {
                                    "type": "object",
                                    "properties": {
                                        "LocalSecondaryIndexes": {
                                            "type": "array",
                                            "minItems": 1,
                                        }
                                    },
                                    "required": ["LocalSecondaryIndexes"],
                                },
                                "then": {
                                    "type": "object",
                                    "properties": {
                                        "KeySchema": {
                                            "minItems": 2,
                                        },
                                        "AttributeDefinitions": {
                                            "minItems": 2,
                                        },
                                    },
                                },
                            }
                        ]
                    },
                    path="/",
                ),
                Patch(
                    values={"enum": ["KMS"]},
                    path="/definitions/SSESpecification/properties/SSEType",
                ),
                Patch(
                    values={"dependentRequired": {"KMSMasterKeyId": ["SSEType"]}},
                    path="/definitions/SSESpecification",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DynamoDB::GlobalTable",
            patches=[
                Patch(
                    values={
                        "allOf": [
                            {
                                "if": {
                                    "required": ["LocalSecondaryIndexes"],
                                    "type": "object",
                                },
                                "then": {
                                    "properties": {
                                        "KeySchema": {
                                            "minItems": 2,
                                        },
                                        "AttributeDefinitions": {
                                            "minItems": 2,
                                        },
                                    },
                                    "type": "object",
                                },
                            }
                        ]
                    },
                    path="/",
                ),
                Patch(
                    values={"enum": ["AES256", "KMS"]},
                    path="/definitions/SSESpecification/properties/SSEType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::DHCPOptions",
            patches=[
                Patch(
                    values={"enum": ["1", "2", "4", "8"]},
                    path="/properties/NetbiosNodeType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::Instance",
            patches=[
                Patch(
                    values=common_patches.get("BlockDeviceMapping"),
                    path="/definitions/BlockDeviceMapping",
                ),
                Patch(
                    values={"pattern": "^ephemeral([0-9]|[1][0-9]|[2][0-3])$"},
                    path="/definitions/BlockDeviceMapping/properties/VirtualName",
                ),
                Patch(
                    values={
                        "dependentExcluded": {
                            "NetworkInterfaces": ["SubnetId"],
                            "SubnetId": ["NetworkInterfaces"],
                        },
                    },
                    path="/",
                ),
                Patch(
                    values={
                        "dependentExcluded": {
                            "AssociateCarrierIpAddress": ["NetworkInterfaceId"],
                            "AssociatePublicIpAddress": ["NetworkInterfaceId"],
                            "NetworkInterfaceId": [
                                "AssociateCarrierIpAddress",
                                "AssociatePublicIpAddress",
                            ],
                        }
                    },
                    path="/definitions/NetworkInterface",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::LaunchTemplate",
            patches=[
                Patch(
                    values=common_patches.get("BlockDeviceMapping"),
                    path="/definitions/BlockDeviceMapping",
                ),
                Patch(
                    values={"pattern": "^ephemeral([0-9]|[1][0-9]|[2][0-3])$"},
                    path="/definitions/BlockDeviceMapping/properties/VirtualName",
                ),
                Patch(
                    values={
                        "dependentExcluded": {
                            "AssociateCarrierIpAddress": ["NetworkInterfaceId"],
                            "AssociatePublicIpAddress": ["NetworkInterfaceId"],
                            "NetworkInterfaceId": [
                                "AssociateCarrierIpAddress",
                                "AssociatePublicIpAddress",
                            ],
                        }
                    },
                    path="/definitions/NetworkInterface",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::NetworkAclEntry",
            patches=[
                Patch(
                    values={
                        "requiredXor": ["Ipv6CidrBlock", "CidrBlock"],
                    },
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::NetworkInterface",
            patches=[
                Patch(
                    values={
                        "dependentExcluded": {
                            "Ipv6AddressCount": ["Ipv6Addresses"],
                            "Ipv6Addresses": ["Ipv6AddressCount"],
                        },
                    },
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::SecurityGroup",
            patches=[
                Patch(
                    path="/",
                    values={"dependentRequired": {"SecurityGroupEgress": ["VpcId"]}},
                ),
                Patch(
                    values={
                        "maxLength": 255,
                        "minLength": 0,
                        "pattern": "^([a-z,A-Z,0-9,. _\\-:/()#,@[\\]+=&;\\{\\}!$*])*$",
                    },
                    path="/properties/GroupDescription",
                ),
                Patch(
                    path="/definitions/Egress",
                    values={
                        "requiredXor": [
                            "CidrIp",
                            "CidrIpv6",
                            "DestinationSecurityGroupId",
                            "DestinationPrefixListId",
                        ]
                    },
                ),
                Patch(
                    path="/definitions/Ingress",
                    values={
                        "requiredXor": [
                            "CidrIp",
                            "CidrIpv6",
                            "SourcePrefixListId",
                            "SourceSecurityGroupId",
                            "SourceSecurityGroupName",
                        ],
                    },
                ),
                Patch(
                    path="/definitions/Ingress/properties/FromPort",
                    values={"minimum": -1},
                ),
                Patch(
                    path="/definitions/Ingress/properties/ToPort",
                    values={"minimum": -1},
                ),
                Patch(
                    path="/definitions/Egress/properties/FromPort",
                    values={"minimum": -1},
                ),
                Patch(
                    path="/definitions/Egress/properties/ToPort", values={"minimum": -1}
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::SecurityGroupEgress",
            patches=[
                Patch(
                    path="/properties/FromPort",
                    values={"minimum": -1},
                ),
                Patch(
                    path="/properties/ToPort",
                    values={"minimum": -1},
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::SecurityGroupIngress",
            patches=[
                Patch(
                    path="/",
                    values={
                        "requiredXor": [
                            "CidrIp",
                            "CidrIpv6",
                            "SourcePrefixListId",
                            "SourceSecurityGroupId",
                            "SourceSecurityGroupName",
                        ],
                    },
                ),
                Patch(
                    path="/properties/FromPort",
                    values={"minimum": -1},
                ),
                Patch(
                    path="/properties/ToPort",
                    values={"minimum": -1},
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::SpotFleet",
            patches=[
                Patch(
                    path="/definitions/BlockDeviceMapping",
                    values=common_patches.get("BlockDeviceMapping"),
                ),
                Patch(
                    values={"pattern": "^ephemeral([0-9]|[1][0-9]|[2][0-3])$"},
                    path="/definitions/BlockDeviceMapping/properties/VirtualName",
                ),
                Patch(
                    path="/definitions/SpotFleetRequestConfigData",
                    values={
                        "requiredXor": ["LaunchSpecifications", "LaunchTemplateConfigs"]
                    },
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::VPC",
            patches=[
                Patch(
                    path="/",
                    values={
                        "requiredXor": ["CidrBlock", "Ipv4IpamPoolId"],
                        "dependentRequired": {
                            "Ipv4IpamPoolId": ["Ipv4NetmaskLength"],
                            "Ipv4NetmaskLength": ["Ipv4IpamPoolId"],
                        },
                    },
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ECS::TaskDefinition",
            patches=[
                Patch(
                    path="/definitions/ContainerDefinition/properties/Environment",
                    values={"uniqueKeys": ["Name"]},
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElastiCache::ReplicationGroup",
            patches=[
                Patch(
                    values={"maximum": 5, "minimum": 0},
                    path="/properties/ReplicasPerNodeGroup",
                ),
                Patch(
                    values={"maximum": 6, "minimum": 1},
                    path="/properties/NumCacheClusters",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElasticLoadBalancingV2::ListenerRule",
            patches=[
                Patch(
                    values={"maximum": 50000, "minimum": 1},
                    path="/properties/Priority",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElasticLoadBalancingV2::LoadBalancer",
            patches=[
                Patch(
                    values={"requiredXor": ["SubnetMappings", "Subnets"]},
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElasticLoadBalancingV2::TargetGroup",
            patches=[
                Patch(
                    values={"maximum": 10, "minimum": 2},
                    path="/properties/UnhealthyThresholdCount",
                ),
                Patch(
                    values={"maximum": 300, "minimum": 5},
                    path="/properties/HealthCheckIntervalSeconds",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Events::EventBusPolicy",
            patches=[
                Patch(
                    values={"enum": ["aws:PrincipalOrgID"]},
                    path="/definitions/Condition/properties/Key",
                ),
                Patch(
                    values={"enum": ["StringEquals"]},
                    path="/definitions/Condition/properties/Type",
                ),
                Patch(
                    values={"enum": ["events:PutEvents"]},
                    path="/properties/Action",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Events::Rule",
            patches=[
                Patch(
                    values={"requiredOr": ["EventPattern", "ScheduleExpression"]},
                    path="/",
                ),
                Patch(
                    values={"maxItems": 5},
                    path="/properties/Targets",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::FSx::FileSystem",
            patches=[
                Patch(
                    values={"maximum": 65536, "minimum": 32},
                    path="/properties/StorageCapacity",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::Job",
            patches=[
                Patch(
                    values={"maximum": 299, "minimum": 0},
                    path="/properties/NumberOfWorkers",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::MLTransform",
            patches=[
                Patch(
                    values={"maximum": 100, "minimum": 1},
                    path="/properties/MaxCapacity",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::Table",
            patches=[
                Patch(
                    values={"enum": ["EXTERNAL_TABLE", "VIRTUAL_VIEW"]},
                    path="/definitions/TableInput/properties/TableType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::Trigger",
            patches=[
                Patch(
                    values={"enum": ["SUCCEEDED", "STOPPED", "TIMEOUT", "FAILED"]},
                    path="/definitions/Condition/properties/State",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::GuardDuty::Member",
            patches=[
                Patch(
                    values={
                        "enum": [
                            "Created",
                            "Disabled",
                            "Enabled",
                            "Invited",
                            "Removed",
                            "Resigned",
                        ]
                    },
                    path="/properties/Status",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::Group",
            patches=[
                Patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
                Patch(
                    # ruff: noqa: E501
                    values={
                        "pattern": "arn:(aws[a-zA-Z-]*)?:iam::(\\d{12}|aws):policy/[a-zA-Z_0-9+=,.@\\-_/]+"
                    },
                    path="/properties/ManagedPolicyArns/items",
                ),
                Patch(
                    values={"maxItems": 20, "minItems": 0},
                    path="/properties/ManagedPolicyArns",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::InstanceProfile",
            patches=[
                Patch(
                    values={"maxItems": 1, "minItems": 1},
                    path="/properties/Roles",
                ),
                Patch(
                    values={"pattern": "[a-zA-Z0-9+=,.@\\-_]+"},
                    path="/properties/Roles/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::ManagedPolicy",
            patches=[
                Patch(
                    values={"maxLength": 6144},
                    path="/properties/PolicyDocument",
                ),
                Patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::Policy",
            patches=[
                Patch(
                    values={
                        "anyOf": [
                            {"required": ["Users"]},
                            {"required": ["Groups"]},
                            {"required": ["Roles"]},
                        ]
                    },
                    path="/",
                ),
                Patch(
                    values={
                        "maxLength": 128,
                        "minLength": 1,
                        "pattern": "^[a-zA-Z0-9+=,.@\\-_]+$",
                    },
                    path="/properties/PolicyName",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::User",
            patches=[
                Patch(
                    values={"maxItems": 10, "minItems": 0},
                    path="/properties/Groups",
                ),
                Patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
                Patch(
                    values={
                        # ruff: noqa: E501
                        "pattern": "arn:(aws[a-zA-Z-]*)?:iam::(\\d{12}|aws):policy/[a-zA-Z_0-9+=,.@\\-_/]+"
                    },
                    path="/properties/ManagedPolicyArns/items",
                ),
                Patch(
                    values={"maxItems": 20, "minItems": 0},
                    path="/properties/ManagedPolicyArns",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::Role",
            patches=[
                Patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
                Patch(
                    values={"maxLength": 2048},
                    path="/properties/AssumeRolePolicyDocument",
                ),
                Patch(
                    values={
                        "pattern": "arn:(aws[a-zA-Z-]*)?:iam::(\\d{12}|aws):policy/[a-zA-Z_0-9+=,.@\\-_/]+"
                    },
                    path="/properties/ManagedPolicyArns/items",
                ),
                Patch(
                    values={"maxItems": 20, "minItems": 0},
                    path="/properties/ManagedPolicyArns",
                ),
                Patch(
                    values={"maxLength": 64, "minLength": 1},
                    path="/properties/RoleName",
                ),
                Patch(
                    values={"maximum": 43200, "minimum": 3600},
                    path="/properties/MaxSessionDuration",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IdentityStore::GroupMembership",
            patches=[
                Patch(
                    values={
                        "maxLength": 47,
                        "minLength": 1,
                        "pattern": "^([0-9a-f]{10}-|)[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$",
                    },
                    path="/definitions/MemberId/properties/UserId",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElasticLoadBalancing::LoadBalancer",
            patches=[
                Patch(
                    values={
                        "enum": ["HTTP", "HTTPS", "TCP", "SSL"],
                    },
                    path="/definitions/Listeners/properties/Protocol",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElasticLoadBalancingV2::Listener",
            patches=[
                Patch(
                    values={
                        "enum": [
                            "GENEVE",
                            "HTTP",
                            "HTTPS",
                            "TCP",
                            "TCP_UDP",
                            "TLS",
                            "UDP",
                        ]
                    },
                    path="/properties/Protocol",
                ),
                Patch(
                    values={"pattern": "^(HTTPS?|#\\{protocol\\})$"},
                    path="/definitions/RedirectConfig/properties/Protocol",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ElasticLoadBalancingV2::LoadBalancer",
            patches=[
                Patch(
                    values={
                        "enum": ["application", "network", "gateway"],
                    },
                    path="/properties/Type",
                ),
                Patch(
                    values={
                        "requiredXor": ["Subnets", "SubnetMappings"],
                    },
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Inspector::AssessmentTemplate",
            patches=[
                Patch(
                    values={"maximum": 86400, "minimum": 180},
                    path="/properties/DurationInSeconds",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Kinesis::Stream",
            patches=[
                Patch(
                    values={"maximum": 100000, "minimum": 1},
                    path="/properties/ShardCount",
                ),
                Patch(
                    values={"maximum": 8760, "minimum": 1},
                    path="/properties/RetentionPeriodHours",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::KMS::Key",
            patches=[
                Patch(
                    values={"maximum": 30, "minimum": 7},
                    path="/properties/PendingWindowInDays",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Lambda::EventSourceMapping",
            patches=[
                Patch(
                    values={"maximum": 10000, "minimum": 1},
                    path="/properties/BatchSize",
                ),
                Patch(
                    values={"maximum": 300, "minimum": 0},
                    path="/properties/MaximumBatchingWindowInSeconds",
                ),
                Patch(
                    values={"maximum": 604800, "minimum": -1},
                    path="/properties/MaximumRecordAgeInSeconds",
                ),
                Patch(
                    values={"maximum": 10000, "minimum": -1},
                    path="/properties/MaximumRetryAttempts",
                ),
                Patch(
                    values={"maximum": 10, "minimum": 1},
                    path="/properties/ParallelizationFactor",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Lambda::Function",
            patches=[
                Patch(
                    values={"maxLength": 256, "minLength": 1},
                    path="/properties/Description",
                ),
                Patch(
                    values={"maxLength": 64, "minLength": 1},
                    path="/properties/FunctionName",
                ),
                Patch(
                    values={"maxLength": 128, "minLength": 1},
                    path="/properties/Handler",
                ),
                Patch(
                    values={"maximum": 10240, "minimum": 128},
                    path="/properties/MemorySize",
                ),
                Patch(
                    values={"maximum": 900, "minimum": 1},
                    path="/properties/Timeout",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Lambda::LayerVersion",
            patches=[
                Patch(
                    values={"maxLength": 140, "minLength": 1},
                    path="/properties/LayerName",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Logs::LogGroup",
            patches=[
                Patch(
                    values={"maxLength": 512, "minLength": 1},
                    path="/properties/LogGroupName",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Logs::MetricFilter",
            patches=[
                Patch(
                    values={"pattern": "^(([0-9]*)|(\\$.*))$"},
                    path="/definitions/MetricTransformation/properties/MetricValue",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::M2::Application",
            patches=[
                Patch(
                    values={"pattern": "^\\S{1,2000}$"},
                    path="/definitions/Definition/oneOf/0/properties/S3Location",
                ),
                Patch(
                    values={"maxLength": 6500, "minLength": 1},
                    path="/definitions/Definition/oneOf/1/properties/Content",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::OpsWorks::Instance",
            patches=[
                Patch(
                    values={"pattern": "^ephemeral([0-9]|[1][0-9]|[2][0-3])$"},
                    path="/definitions/BlockDeviceMapping/properties/VirtualName",
                ),
                Patch(
                    values=common_patches.get("BlockDeviceMapping"),
                    path="/definitions/BlockDeviceMapping",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::OpsWorks::Stack",
            patches=[
                Patch(
                    path="/",
                    values={"dependentRequired": {"VpcId": ["DefaultSubnetId"]}},
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::RDS::DBCluster",
            patches=[
                Patch(
                    values={"maximum": 35},
                    path="/properties/BackupRetentionPeriod",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::RDS::DBInstance",
            patches=[
                Patch(
                    values={"maximum": 15},
                    path="/properties/PromotionTier",
                ),
                Patch(
                    values={"maximum": 35},
                    path="/properties/BackupRetentionPeriod",
                ),
                Patch(
                    values={
                        "enum": [
                            7,
                            31,
                            62,
                            93,
                            124,
                            155,
                            186,
                            217,
                            248,
                            279,
                            310,
                            341,
                            372,
                            403,
                            434,
                            465,
                            496,
                            527,
                            558,
                            589,
                            620,
                            651,
                            682,
                            713,
                            731,
                        ]
                    },
                    path="/properties/PerformanceInsightsRetentionPeriod",
                ),
                Patch(
                    values={
                        "dependentExcluded": {
                            "SourceDBInstanceIdentifier": [
                                "CharacterSetName",
                                "MasterUserPassword",
                                "MasterUsername",
                                "StorageEncrypted",
                            ]
                        },
                        "dependencies": {
                            "KmsKeyId": {
                                "properties": {
                                    "StorageEncrypted": {"enum": ["true", "True", True]}
                                },
                                "required": ["StorageEncrypted"],
                            },
                        },
                    },
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::RDS::DBProxyEndpoint",
            patches=[
                Patch(
                    values={"enum": ["READ_WRITE", "READ_ONLY"]},
                    path="/properties/TargetRole",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Redshift::Cluster",
            patches=[
                Patch(
                    values={"maximum": 100, "minimum": 1},
                    path="/properties/NumberOfNodes",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Route53::RecordSet",
            patches=[
                Patch(
                    values={"requiredXor": ["HostedZoneId", "HostedZoneName"]},
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Route53::RecordSetGroup",
            patches=[
                Patch(
                    values={"requiredXor": ["HostedZoneId", "HostedZoneName"]},
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::S3::Bucket",
            patches=[
                Patch(
                    values={
                        "maxLength": 63,
                        "minLength": 3,
                        "pattern": "^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
                    },
                    path="/properties/BucketName",
                ),
                Patch(
                    values={
                        "anyOf": [
                            {"required": ["HttpErrorCodeReturnedEquals"]},
                            {"required": ["KeyPrefixEquals"]},
                        ],
                    },
                    path="/definitions/RoutingRuleCondition",
                ),
                Patch(
                    values={
                        "dependentExcluded": {
                            "RedirectAllRequestsTo": [
                                "ErrorDocument",
                                "IndexDocument",
                                "RoutingRules",
                            ],
                        }
                    },
                    path="/definitions/RedirectAllRequestsTo",
                ),
                Patch(
                    values={
                        "dependentExcluded": {
                            "ObjectSizeLessThan": ["AbortIncompleteMultipartUpload"],
                            "ObjectSizeGreaterThan": ["AbortIncompleteMultipartUpload"],
                        },
                    },
                    path="/definitions/Rule",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::SageMaker::NotebookInstance",
            patches=[
                Patch(
                    values={"maximum": 16384, "minimum": 5},
                    path="/properties/VolumeSizeInGB",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ServiceDiscovery::Service",
            patches=[
                Patch(
                    values={
                        "dependentExcluded": {
                            "HealthCheckConfig": ["HealthCheckCustomConfig"],
                            "HealthCheckCustomConfig": ["HealthCheckConfig"],
                        }
                    },
                    path="/",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::SNS::Topic",
            patches=[
                Patch(
                    values={"maxLength": 256, "minLength": 1},
                    path="/properties/TopicName",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::SQS::Queue",
            patches=[
                Patch(
                    values={"maximum": 1209600, "minimum": 60},
                    path="/properties/MessageRetentionPeriod",
                ),
                Patch(
                    values={"maximum": 900, "minimum": 0},
                    path="/properties/DelaySeconds",
                ),
                Patch(
                    values={"maximum": 20, "minimum": 0},
                    path="/properties/ReceiveMessageWaitTimeSeconds",
                ),
                Patch(
                    values={"maximum": 86400, "minimum": 60},
                    path="/properties/KmsDataKeyReusePeriodSeconds",
                ),
                Patch(
                    values={"maximum": 43200, "minimum": 0},
                    path="/properties/VisibilityTimeout",
                ),
                Patch(
                    values={"maximum": 262144, "minimum": 1024},
                    path="/properties/MaximumMessageSize",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::SSM::MaintenanceWindow",
            patches=[
                Patch(
                    values={"maximum": 24, "minimum": 1},
                    path="/properties/Duration",
                ),
                Patch(
                    values={"maximum": 23, "minimum": 0},
                    path="/properties/Cutoff",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::WAFRegional::RegexPatternSet",
            patches=[
                Patch(
                    values={"maxLength": 200, "minLength": 0},
                    path="/properties/RegexPatternStrings/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::WAFv2::RegexPatternSet",
            patches=[
                Patch(
                    values={"maxLength": 200, "minLength": 0},
                    path="/properties/RegularExpressionList/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::Subnet",
            patches=[
                Patch(
                    values={
                        "requiredXor": ["CidrBlock", "Ipv4IpamPoolId"],
                        "dependentExcluded": {
                            "AvailabilityZone": ["AvailabilityZoneId"],
                            "AvailabilityZoneId": ["AvailabilityZone"],
                        },
                        "dependentRequired": {
                            "Ipv4IpamPoolId": ["Ipv4NetmaskLength"],
                            "Ipv4NetmaskLength": ["Ipv4IpamPoolId"],
                        },
                    },
                    path="/",
                ),
            ],
        ),
    ]
)


def configure_logging():
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    LOGGER.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def build_resource_type_patches(resource_patches: ResourcePatch, filename: str):
    LOGGER.info(f"Applying patches for {resource_patches.resource_type}")

    resource_name = resource_patches.resource_type.lower().replace("::", "_")
    output_dir = os.path.join(
        "src/cfnlint/data/schemas/patches/extensions/all/", resource_name
    )
    output_file = os.path.join(output_dir, filename)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        with open(os.path.join(output_dir, "__init__.py"), "w"):
            pass

    d = []
    with open(output_file, "w+") as fh:
        for patch in resource_patches.patches:
            for k, v in patch.values.items():
                d.append(
                    {
                        "op": "add",
                        "path": f"{patch.path if not patch.path == '/' else ''}/{k}",
                        "value": v,
                    }
                )
        json.dump(
            d,
            fh,
            indent=1,
            separators=(",", ": "),
            sort_keys=True,
        )
        fh.write("\n")


def build_patches(patches, filename):
    for patch in patches:
        build_resource_type_patches(resource_patches=patch, filename=filename)


def main():
    """main function"""
    configure_logging()
    build_patches(patches, "manual.json")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
