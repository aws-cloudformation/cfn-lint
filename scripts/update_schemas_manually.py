#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

"""
    Updates our patches from boto enums
"""
from typing import List
import json
import logging
import os
from collections import namedtuple

LOGGER = logging.getLogger("cfnlint")

patch = namedtuple("Patch", ["values", "path"])
resource_patch = namedtuple("ResourcePatch", ["resource_type", "patches"])
patches: List[resource_patch] = []
patches.extend(
    [
        resource_patch(
            resource_type="AWS::AppStream::Fleet",
            patches=[
                patch(
                    values={"maximum": 360000, "minimum": 60},
                    path="/properties/DisconnectTimeoutInSeconds",
                ),
                patch(
                    values={"maximum": 3600, "minimum": 0},
                    path="/properties/IdleDisconnectTimeoutInSeconds",
                ),
                patch(
                    values={"maximum": 360000, "minimum": 600},
                    path="/properties/MaxUserDurationInSeconds",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AutoScaling::AutoScalingGroup",
            patches=[
                patch(
                    values={"enum": ["EC2", "ELB"]},
                    path="/properties/HealthCheckType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AutoScaling::LifecycleHook",
            patches=[
                patch(
                    values={"enum": ["ABANDON", "CONTINUE"]},
                    path="/properties/DefaultResult",
                ),
                patch(
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
        resource_patch(
            resource_type="AWS::AutoScaling::ScalingPolicy",
            patches=[
                patch(
                    values={
                        "enum": [
                            "ChangeInCapacity",
                            "ExactCapacity",
                            "PercentChangeInCapacity",
                        ]
                    },
                    path="/properties/AdjustmentType",
                ),
                patch(
                    values={"enum": ["Average", "Maximum", "Minimum"]},
                    path="/properties/MetricAggregationType",
                ),
                patch(
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
        resource_patch(
            resource_type="AWS::Budgets::Budget",
            patches=[
                patch(
                    values={
                        "maximum": 1000000000,
                        "minimum": 0.1,
                    },
                    path="/definitions/Notification/properties/Threshold",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CloudFormation::WaitCondition",
            patches=[
                patch(
                    values={"maximum": 43200, "minimum": 0},
                    path="/properties/Timeout",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CloudFront::Distribution",
            patches=[
                patch(
                    values={
                        "enum": [400, 403, 404, 405, 414, 416, 500, 501, 502, 503, 504]
                    },
                    path="/definitions/CustomErrorResponse/properties/ErrorCode",
                ),
                patch(
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
                patch(
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
        resource_patch(
            resource_type="AWS::CloudTrail::Trail",
            patches=[
                patch(
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
        resource_patch(
            resource_type="AWS::CloudWatch::Alarm",
            patches=[
                patch(
                    values={"maximum": 1024, "minimum": 1},
                    path="/properties/AlarmActions/items",
                ),
                patch(
                    values={"maxItems": 5, "minItems": 0},
                    path="/properties/AlarmActions",
                ),
                patch(
                    values={"pattern": "^([a-z])([A-Za-z0-9\\_]*)$"},
                    path="/definitions/MetricDataQuery/properties/Id",
                ),
                patch(
                    values={"enum": ["breaching", "ignore", "missing", "notBreaching"]},
                    path="/properties/TreatMissingData",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeBuild::Project",
            patches=[
                patch(
                    values={"maximum": 480, "minimum": 5},
                    path="/properties/QueuedTimeoutInMinutes",
                ),
                patch(
                    values={"maximum": 480, "minimum": 5},
                    path="/properties/TimeoutInMinutes",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                patch(
                    values={
                        "maximum": 100,
                        "minimum": 1,
                        "pattern": "^[a-zA-Z0-9._\\-]+(?<!\\.git)$",
                    },
                    path="/properties/RepositoryName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                patch(
                    values={
                        "maximum": 100,
                        "minimum": 1,
                        "pattern": "^[a-zA-Z0-9._\\-]+(?<!\\.git)$",
                    },
                    path="/properties/RepositoryName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Cognito::UserPoolClient",
            patches=[
                patch(
                    values={
                        "maximum": 3650,
                        "minimum": 0,
                    },
                    path="/properties/RefreshTokenValidity",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Config::ConfigRule",
            patches=[
                patch(
                    values={"maxLength": 256, "minLength": 1},
                    path="/properties/Description",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::DocDB::DBCluster",
            patches=[
                patch(
                    values={"enum": ["3.6.0", "4.0", "4.0.0"]},
                    path="/properties/EngineVersion",
                ),
                patch(
                    values={"maximum": 35, "minimum": 1},
                    path="/properties/BackupRetentionPeriod",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::EC2::DHCPOptions",
            patches=[
                patch(
                    values={"enum": ["1", "2", "4", "8"]},
                    path="/properties/NetbiosNodeType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::EC2::SecurityGroup",
            patches=[
                patch(
                    values={
                        "maxLength": 255,
                        "minLength": 0,
                        "pattern": "^([a-z,A-Z,0-9,. _\\-:/()#,@[\\]+=&;\\{\\}!$*])*$",
                    },
                    path="/properties/GroupDescription",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ElastiCache::ReplicationGroup",
            patches=[
                patch(
                    values={"maximum": 5, "minimum": 0},
                    path="/properties/ReplicasPerNodeGroup",
                ),
                patch(
                    values={"maximum": 6, "minimum": 1},
                    path="/properties/NumCacheClusters",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ElasticLoadBalancingV2::ListenerRule",
            patches=[
                patch(
                    values={"maximum": 50000, "minimum": 1},
                    path="/properties/Priority",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ElasticLoadBalancingV2::TargetGroup",
            patches=[
                patch(
                    values={"maximum": 10, "minimum": 2},
                    path="/properties/UnhealthyThresholdCount",
                ),
                patch(
                    values={"maximum": 300, "minimum": 5},
                    path="/properties/HealthCheckIntervalSeconds",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Events::EventBusPolicy",
            patches=[
                patch(
                    values={"enum": ["aws:PrincipalOrgID"]},
                    path="/definitions/Condition/properties/Key",
                ),
                patch(
                    values={"enum": ["StringEquals"]},
                    path="/definitions/Condition/properties/Type",
                ),
                patch(
                    values={"enum": ["events:PutEvents"]},
                    path="/properties/Action",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::FSx::FileSystem",
            patches=[
                patch(
                    values={"maximum": 65536, "minimum": 32},
                    path="/properties/StorageCapacity",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::Job",
            patches=[
                patch(
                    values={"maximum": 299, "minimum": 0},
                    path="/properties/NumberOfWorkers",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::MLTransform",
            patches=[
                patch(
                    values={"maximum": 100, "minimum": 1},
                    path="/properties/MaxCapacity",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::Table",
            patches=[
                patch(
                    values={"enum": ["EXTERNAL_TABLE", "VIRTUAL_VIEW"]},
                    path="/definitions/TableInput/properties/TableType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::Trigger",
            patches=[
                patch(
                    values={"enum": ["SUCCEEDED", "STOPPED", "TIMEOUT", "FAILED"]},
                    path="/definitions/Condition/properties/State",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::GuardDuty::Member",
            patches=[
                patch(
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
        resource_patch(
            resource_type="AWS::IAM::Group",
            patches=[
                patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
                patch(
                    values={
                        "pattern": "arn:(aws[a-zA-Z-]*)?:iam::(\\d{12}|aws):policy/[a-zA-Z_0-9+=,.@\\-_/]+"
                    },
                    path="/properties/ManagedPolicyArns/items",
                ),
                patch(
                    values={"maxItems": 20, "minItems": 0},
                    path="/properties/ManagedPolicyArns",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IAM::InstanceProfile",
            patches=[
                patch(
                    values={"maxItems": 1, "minItems": 1},
                    path="/properties/Roles",
                ),
                patch(
                    values={"pattern": "[a-zA-Z0-9+=,.@\\-_]+"},
                    path="/properties/Roles/items",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IAM::ManagedPolicy",
            patches=[
                patch(
                    values={"maxLength": 6144},
                    path="/properties/PolicyDocument",
                ),
                patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IAM::Policy",
            patches=[
                patch(
                    values={
                        "maxLength": 128,
                        "minLength": 1,
                        "pattern": "^[a-zA-Z0-9+=,.@\\-_]+$",
                    },
                    path="/properties/PolicyName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IAM::User",
            patches=[
                patch(
                    values={"maxItems": 10, "minItems": 0},
                    path="/properties/Groups",
                ),
                patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
                patch(
                    values={
                        "pattern": "arn:(aws[a-zA-Z-]*)?:iam::(\\d{12}|aws):policy/[a-zA-Z_0-9+=,.@\\-_/]+"
                    },
                    path="/properties/ManagedPolicyArns/items",
                ),
                patch(
                    values={"maxItems": 20, "minItems": 0},
                    path="/properties/ManagedPolicyArns",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IAM::Role",
            patches=[
                patch(
                    values={"pattern": "^/(.+/)*$"},
                    path="/properties/Path",
                ),
                patch(
                    values={"maxLength": 2048},
                    path="/properties/AssumeRolePolicyDocument",
                ),
                patch(
                    values={
                        "pattern": "arn:(aws[a-zA-Z-]*)?:iam::(\\d{12}|aws):policy/[a-zA-Z_0-9+=,.@\\-_/]+"
                    },
                    path="/properties/ManagedPolicyArns/items",
                ),
                patch(
                    values={"maxItems": 20, "minItems": 0},
                    path="/properties/ManagedPolicyArns",
                ),
                patch(
                    values={"maxLength": 64, "minLength": 1},
                    path="/properties/RoleName",
                ),
                patch(
                    values={"maximum": 43200, "minimum": 3600},
                    path="/properties/MaxSessionDuration",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IdentityStore::GroupMembership",
            patches=[
                patch(
                    values={
                        "maxLength": 47,
                        "minLength": 1,
                        "pattern": "^([0-9a-f]{10}-|)[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}$",
                    },
                    path="/definitions/MemberId/properties/UserId",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Inspector::AssessmentTemplate",
            patches=[
                patch(
                    values={"maximum": 86400, "minimum": 180},
                    path="/properties/DurationInSeconds",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Kinesis::Stream",
            patches=[
                patch(
                    values={"maximum": 100000, "minimum": 1},
                    path="/properties/ShardCount",
                ),
                patch(
                    values={"maximum": 8760, "minimum": 1},
                    path="/properties/RetentionPeriodHours",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::KMS::Key",
            patches=[
                patch(
                    values={"maximum": 30, "minimum": 7},
                    path="/properties/PendingWindowInDays",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Lambda::EventSourceMapping",
            patches=[
                patch(
                    values={"maximum": 10000, "minimum": 1},
                    path="/properties/BatchSize",
                ),
                patch(
                    values={"maximum": 300, "minimum": 0},
                    path="/properties/MaximumBatchingWindowInSeconds",
                ),
                patch(
                    values={"maximum": 604800, "minimum": -1},
                    path="/properties/MaximumRecordAgeInSeconds",
                ),
                patch(
                    values={"maximum": 10000, "minimum": -1},
                    path="/properties/MaximumRetryAttempts",
                ),
                patch(
                    values={"maximum": 10, "minimum": 1},
                    path="/properties/ParallelizationFactor",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Lambda::Function",
            patches=[
                patch(
                    values={"maxLength": 256, "minLength": 1},
                    path="/properties/Description",
                ),
                patch(
                    values={"maxLength": 64, "minLength": 1},
                    path="/properties/FunctionName",
                ),
                patch(
                    values={"maxLength": 128, "minLength": 1},
                    path="/properties/Handler",
                ),
                patch(
                    values={"maximum": 10240, "minimum": 128},
                    path="/properties/MemorySize",
                ),
                patch(
                    values={"maximum": 900, "minimum": 1},
                    path="/properties/Timeout",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Lambda::LayerVersion",
            patches=[
                patch(
                    values={"maxLength": 140, "minLength": 1},
                    path="/properties/LayerName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Logs::LogGroup",
            patches=[
                patch(
                    values={"maxLength": 512, "minLength": 1},
                    path="/properties/LogGroupName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Logs::MetricFilter",
            patches=[
                patch(
                    values={"pattern": "^(([0-9]*)|(\\$.*))$"},
                    path="/definitions/MetricTransformation/properties/MetricValue",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::M2::Application",
            patches=[
                patch(
                    values={"pattern": "^\\S{1,2000}$"},
                    path="/definitions/Definition/oneOf/0/properties/S3Location",
                ),
                patch(
                    values={"maxLength": 6500, "minLength": 1},
                    path="/definitions/Definition/oneOf/1/properties/Content",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::RDS::DBCluster",
            patches=[
                patch(
                    values={"maximum": 35, "minimum": 1},
                    path="/properties/BackupRetentionPeriod",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::RDS::DBInstance",
            patches=[
                patch(
                    values={"maximum": 15, "minimum": 0},
                    path="/properties/PromotionTier",
                ),
                patch(
                    values={"maximum": 35, "minimum": 1},
                    path="/properties/BackupRetentionPeriod",
                ),
                patch(
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
            ],
        ),
        resource_patch(
            resource_type="AWS::RDS::DBProxyEndpoint",
            patches=[
                patch(
                    values={"enum": ["READ_WRITE", "READ_ONLY"]},
                    path="/properties/TargetRole",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Redshift::Cluster",
            patches=[
                patch(
                    values={"maximum": 100, "minimum": 1},
                    path="/properties/NumberOfNodes",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::S3::Bucket",
            patches=[
                patch(
                    values={
                        "maxLength": 63,
                        "minLength": 3,
                        "pattern": "^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
                    },
                    path="/properties/BucketName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::SageMaker::NotebookInstance",
            patches=[
                patch(
                    values={"maximum": 16384, "minimum": 5},
                    path="/properties/VolumeSizeInGB",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::SNS::Topic",
            patches=[
                patch(
                    values={"maxLength": 256, "minLength": 1},
                    path="/properties/TopicName",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::SQS::Queue",
            patches=[
                patch(
                    values={"maximum": 1209600, "minimum": 1024},
                    path="/properties/MessageRetentionPeriod",
                ),
                patch(
                    values={"maximum": 900, "minimum": 0},
                    path="/properties/DelaySeconds",
                ),
                patch(
                    values={"maximum": 20, "minimum": 0},
                    path="/properties/ReceiveMessageWaitTimeSeconds",
                ),
                patch(
                    values={"maximum": 86400, "minimum": 60},
                    path="/properties/KmsDataKeyReusePeriodSeconds",
                ),
                patch(
                    values={"maximum": 43200, "minimum": 0},
                    path="/properties/VisibilityTimeout",
                ),
                patch(
                    values={"maximum": 262144, "minimum": 1024},
                    path="/properties/MaximumMessageSize",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::SSM::MaintenanceWindow",
            patches=[
                patch(
                    values={"maximum": 24, "minimum": 1},
                    path="/properties/Duration",
                ),
                patch(
                    values={"maximum": 23, "minimum": 0},
                    path="/properties/Cutoff",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::WAFRegional::RegexPatternSet",
            patches=[
                patch(
                    values={"maxLength": 200, "minLength": 0},
                    path="/properties/RegexPatternStrings/items",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::WAFv2::RegexPatternSet",
            patches=[
                patch(
                    values={"maxLength": 200, "minLength": 0},
                    path="/properties/RegularExpressionList/items",
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


def build_resource_type_patches(resource_patches: resource_patch):
    LOGGER.info(f"Applying patches for {resource_patches.resource_type}")

    resource_name = resource_patches.resource_type.lower().replace("::", "_")
    output_dir = os.path.join("src/cfnlint/data/schemas/patches/extensions/all/")
    output_file = os.path.join(
        output_dir,
        resource_name,
        "manual.json",
    )

    d = []
    with open(output_file, "w+") as fh:
        for patch in resource_patches.patches:
            for k, v in patch.values.items():
                d.append(
                    {
                        "op": "add",
                        "path": f"{patch.path}/{k}",
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


def build_patches():
    for patch in patches:
        build_resource_type_patches(resource_patches=patch)


def main():
    """main function"""
    configure_logging()
    build_patches()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        LOGGER.error(ValueError)
