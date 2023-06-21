#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import io
import json
import logging
import os
import tempfile
import zipfile
from collections import namedtuple
from typing import List

import requests

LOGGER = logging.getLogger("cfnlint")

BOTO_URL = "https://github.com/boto/botocore/archive/refs/heads/master.zip"

Patch = namedtuple("Patch", ["source", "shape", "path"])
ResourcePatch = namedtuple("ResourcePatch", ["resource_type", "patches"])
patches: List[ResourcePatch] = []
patches.extend(
    [
        ResourcePatch(
            resource_type="AWS::AmazonMQ::Broker",
            patches=[
                Patch(
                    source=["mq", "2017-11-27"],
                    shape="DeploymentMode",
                    path="/properties/DeploymentMode",
                ),
                Patch(
                    source=["mq", "2017-11-27"],
                    shape="EngineType",
                    path="/properties/EngineType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ApiGateway::RestApi",
            patches=[
                Patch(
                    source=["apigateway", "2015-07-09"],
                    shape="ApiKeySourceType",
                    path="/properties/ApiKeySourceType",
                )
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ApiGateway::Authorizer",
            patches=[
                Patch(
                    source=["apigateway", "2015-07-09"],
                    shape="AuthorizerType",
                    path="/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ApiGateway::GatewayResponse",
            patches=[
                Patch(
                    source=["apigateway", "2015-07-09"],
                    shape="GatewayResponseType",
                    path="/properties/ResponseType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ApplicationAutoScaling::ScalingPolicy",
            patches=[
                Patch(
                    source=["application-autoscaling", "2016-02-06"],
                    shape="PolicyType",
                    path="/properties/PolicyType",
                ),
                Patch(
                    source=["application-autoscaling", "2016-02-06"],
                    shape="MetricType",
                    path="/definitions/PredefinedMetricSpecification/properties/PredefinedMetricType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AppSync::DataSource",
            patches=[
                Patch(
                    source=["appsync", "2017-07-25"],
                    shape="DataSourceType",
                    path="/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AppSync::GraphQLApi",
            patches=[
                Patch(
                    source=["appsync", "2017-07-25"],
                    shape="AuthenticationType",
                    path="/properties/AuthenticationType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AppSync::Resolver",
            patches=[
                Patch(
                    source=["appsync", "2017-07-25"],
                    shape="ResolverKind",
                    path="/properties/Kind",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScaling::LaunchConfiguration",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="VolumeType",
                    path="/definitions/BlockDevice/properties/VolumeType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScaling::ScalingPolicy",
            patches=[
                Patch(
                    source=["autoscaling", "2011-01-01"],
                    shape="MetricStatistic",
                    path="/definitions/CustomizedMetricSpecification/properties/Statistic",
                ),
                Patch(
                    source=["autoscaling", "2011-01-01"],
                    shape="MetricType",
                    path="/definitions/PredefinedMetricSpecification/properties/PredefinedMetricType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::AutoScalingPlans::ScalingPlan",
            patches=[
                Patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="ScalableDimension",
                    path="/definitions/ScalingInstruction/properties/ScalableDimension",
                ),
                Patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="ServiceNamespace",
                    path="/definitions/ScalingInstruction/properties/ServiceNamespace",
                ),
                Patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="PredictiveScalingMaxCapacityBehavior",
                    path="/definitions/ScalingInstruction/properties/PredictiveScalingMaxCapacityBehavior",
                ),
                Patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="PredictiveScalingMode",
                    path="/definitions/ScalingInstruction/properties/PredictiveScalingMode",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Budgets::Budget",
            patches=[
                Patch(
                    source=["budgets", "2016-10-20"],
                    shape="BudgetType",
                    path="/definitions/BudgetData/properties/BudgetType",
                ),
                Patch(
                    source=["budgets", "2016-10-20"],
                    shape="TimeUnit",
                    path="/definitions/BudgetData/properties/TimeUnit",
                ),
                Patch(
                    source=["budgets", "2016-10-20"],
                    shape="ComparisonOperator",
                    path="/definitions/Notification/properties/ComparisonOperator",
                ),
                Patch(
                    source=["budgets", "2016-10-20"],
                    shape="NotificationType",
                    path="/definitions/Notification/properties/NotificationType",
                ),
                Patch(
                    source=["budgets", "2016-10-20"],
                    shape="ThresholdType",
                    path="/definitions/Notification/properties/ThresholdType",
                ),
                Patch(
                    source=["budgets", "2016-10-20"],
                    shape="SubscriptionType",
                    path="/definitions/Subscriber/properties/SubscriptionType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CertificateManager::Certificate",
            patches=[
                Patch(
                    source=["acm", "2015-12-08"],
                    shape="ValidationMethod",
                    path="/properties/ValidationMethod",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudFormation::StackSet",
            patches=[
                Patch(
                    source=["cloudformation", "2010-05-15"],
                    shape="PermissionModels",
                    path="/properties/PermissionModel",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudFront::Distribution",
            patches=[
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="ViewerProtocolPolicy",
                    path="/definitions/CacheBehavior/properties/ViewerProtocolPolicy",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="GeoRestrictionType",
                    path="/definitions/GeoRestriction/properties/RestrictionType",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="HttpVersion",
                    path="/definitions/DistributionConfig/properties/HttpVersion",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="EventType",
                    path="/definitions/FunctionAssociation/properties/EventType",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="OriginProtocolPolicy",
                    path="/definitions/LegacyCustomOrigin/properties/OriginProtocolPolicy",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="SslProtocol",
                    path="/definitions/CustomOriginConfig/properties/OriginSSLProtocols/items",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="SslProtocol",
                    path="/definitions/LegacyCustomOrigin/properties/OriginSSLProtocols/items",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="PriceClass",
                    path="/definitions/DistributionConfig/properties/PriceClass",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="MinimumProtocolVersion",
                    path="/definitions/ViewerCertificate/properties/MinimumProtocolVersion",
                ),
                Patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="SSLSupportMethod",
                    path="/definitions/ViewerCertificate/properties/SslSupportMethod",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CloudWatch::Alarm",
            patches=[
                Patch(
                    source=["cloudwatch", "2010-08-01"],
                    shape="ComparisonOperator",
                    path="/properties/ComparisonOperator",
                ),
                Patch(
                    source=["cloudwatch", "2010-08-01"],
                    shape="Statistic",
                    path="/properties/Statistic",
                ),
                Patch(
                    source=["cloudwatch", "2010-08-01"],
                    shape="StandardUnit",
                    path="/properties/Unit",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeBuild::Project",
            patches=[
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ArtifactPackaging",
                    path="/definitions/Artifacts/properties/Packaging",
                ),
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ArtifactsType",
                    path="/definitions/Artifacts/properties/Type",
                ),
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ComputeType",
                    path="/definitions/Environment/properties/ComputeType",
                ),
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ImagePullCredentialsType",
                    path="/definitions/Environment/properties/ImagePullCredentialsType",
                ),
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="EnvironmentType",
                    path="/definitions/Environment/properties/Type",
                ),
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="CacheType",
                    path="/definitions/ProjectCache/properties/Type",
                ),
                Patch(
                    source=["codebuild", "2016-10-06"],
                    shape="SourceType",
                    path="/definitions/Source/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                Patch(
                    source=["codecommit", "2015-04-13"],
                    shape="RepositoryTriggerEventEnum",
                    path="/definitions/RepositoryTrigger/properties/Events/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                Patch(
                    source=["codecommit", "2015-04-13"],
                    shape="RepositoryTriggerEventEnum",
                    path="/definitions/RepositoryTrigger/properties/Events/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeDeploy::Application",
            patches=[
                Patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="ComputePlatform",
                    path="/properties/ComputePlatform",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeDeploy::DeploymentGroup",
            patches=[
                Patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="AutoRollbackEvent",
                    path="/definitions/AutoRollbackConfiguration/properties/Events/items",
                ),
                Patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="DeploymentOption",
                    path="/definitions/DeploymentStyle/properties/DeploymentOption",
                ),
                Patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="DeploymentType",
                    path="/definitions/DeploymentStyle/properties/DeploymentType",
                ),
                Patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="TriggerEventType",
                    path="/definitions/TriggerConfig/properties/TriggerEvents/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodeDeploy::DeploymentConfig",
            patches=[
                Patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="MinimumHealthyHostsType",
                    path="/definitions/MinimumHealthyHosts/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodePipeline::Pipeline",
            patches=[
                Patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ActionCategory",
                    path="/definitions/ActionTypeId/properties/Category",
                ),
                Patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ActionOwner",
                    path="/definitions/ActionTypeId/properties/Owner",
                ),
                Patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ArtifactStoreType",
                    path="/definitions/ArtifactStore/properties/Type",
                ),
                Patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="BlockerType",
                    path="/definitions/BlockerDeclaration/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodePipeline::CustomActionType",
            patches=[
                Patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ActionConfigurationPropertyType",
                    path="/definitions/ConfigurationProperties/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::CodePipeline::Webhook",
            patches=[
                Patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="WebhookAuthenticationType",
                    path="/properties/Authentication",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Cognito::UserPool",
            patches=[
                Patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="AliasAttributeType",
                    path="/properties/AliasAttributes/items",
                ),
                Patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="UsernameAttributeType",
                    path="/properties/UsernameAttributes/items",
                ),
                Patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="UserPoolMfaType",
                    path="/properties/MfaConfiguration",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Cognito::UserPoolUser",
            patches=[
                Patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="DeliveryMediumType",
                    path="/properties/DesiredDeliveryMediums/items",
                ),
                Patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="MessageActionType",
                    path="/properties/MessageAction",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Cognito::UserPoolClient",
            patches=[
                Patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="ExplicitAuthFlowsType",
                    path="/properties/ExplicitAuthFlows/items",
                )
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Config::ConfigRule",
            patches=[
                Patch(
                    source=["config", "2014-11-12"],
                    shape="Owner",
                    path="/definitions/Source/properties/Owner",
                ),
                Patch(
                    source=["config", "2014-11-12"],
                    shape="EventSource",
                    path="/definitions/SourceDetail/properties/EventSource",
                ),
                Patch(
                    source=["config", "2014-11-12"],
                    shape="MaximumExecutionFrequency",
                    path="/definitions/SourceDetail/properties/MaximumExecutionFrequency",
                ),
                Patch(
                    source=["config", "2014-11-12"],
                    shape="MessageType",
                    path="/definitions/SourceDetail/properties/MessageType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DirectoryService::MicrosoftAD",
            patches=[
                Patch(
                    source=["ds", "2015-04-16"],
                    shape="DirectoryEdition",
                    path="/properties/Edition",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DirectoryService::SimpleAD",
            patches=[
                Patch(
                    source=["ds", "2015-04-16"],
                    shape="DirectorySize",
                    path="/properties/Size",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DLM::LifecyclePolicy",
            patches=[
                Patch(
                    source=["dlm", "2018-01-12"],
                    shape="ResourceTypeValues",
                    path="/definitions/PolicyDetails/properties/ResourceTypes/items",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DMS::Endpoint",
            patches=[
                Patch(
                    source=["dms", "2016-01-01"],
                    shape="DmsSslModeValue",
                    path="/properties/SslMode",
                ),
                Patch(
                    source=["dms", "2016-01-01"],
                    shape="ReplicationEndpointTypeValue",
                    path="/properties/EndpointType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::DynamoDB::Table",
            patches=[
                Patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="ScalarAttributeType",
                    path="/definitions/AttributeDefinition/properties/AttributeType",
                ),
                Patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="BillingMode",
                    path="/properties/BillingMode",
                ),
                Patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="KeyType",
                    path="/definitions/KeySchema/properties/KeyType",
                ),
                Patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="ProjectionType",
                    path="/definitions/Projection/properties/ProjectionType",
                ),
                Patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="StreamViewType",
                    path="/definitions/StreamSpecification/properties/StreamViewType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::CapacityReservation",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="EndDateType",
                    path="/properties/EndDateType",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="InstanceMatchCriteria",
                    path="/properties/InstanceMatchCriteria",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="CapacityReservationInstancePlatform",
                    path="/properties/InstancePlatform",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::CustomerGateway",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="GatewayType",
                    path="/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::EIP",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="DomainType",
                    path="/properties/Domain",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::EC2Fleet",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="FleetOnDemandAllocationStrategy",
                    path="/definitions/OnDemandOptionsRequest/properties/AllocationStrategy",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::Host",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="AutoPlacement",
                    path="/properties/AutoPlacement",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::Instance",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="Affinity",
                    path="/properties/Affinity",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="Tenancy",
                    path="/properties/Tenancy",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::LaunchTemplate",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="ShutdownBehavior",
                    path="/definitions/LaunchTemplateData/properties/InstanceInitiatedShutdownBehavior",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="MarketType",
                    path="/definitions/InstanceMarketOptions/properties/MarketType",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="SpotInstanceInterruptionBehavior",
                    path="/definitions/SpotOptions/properties/InstanceInterruptionBehavior",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="SpotInstanceType",
                    path="/definitions/SpotOptions/properties/SpotInstanceType",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="VolumeType",
                    path="/definitions/Ebs/properties/VolumeType",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="Tenancy",
                    path="/definitions/Placement/properties/Tenancy",
                ),
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="ResourceType",
                    path="/definitions/TagSpecification/properties/ResourceType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::NetworkAclEntry",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="RuleAction",
                    path="/properties/RuleAction",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::NetworkInterfacePermission",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="InterfacePermissionType",
                    path="/properties/Permission",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::PlacementGroup",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="PlacementGroupStrategy",
                    path="/properties/Strategy",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EC2::SpotFleet",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="VolumeType",
                    path="/definitions/EbsBlockDevice/properties/VolumeType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ECS::TaskDefinition",
            patches=[
                Patch(
                    source=["ecs", "2014-11-13"],
                    shape="NetworkMode",
                    path="/properties/NetworkMode",
                ),
                Patch(
                    source=["ecs", "2014-11-13"],
                    shape="ProxyConfigurationType",
                    path="/definitions/ProxyConfiguration/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::EFS::FileSystem",
            patches=[
                Patch(
                    source=["efs", "2015-02-01"],
                    shape="TransitionToIARules",
                    path="/definitions/LifecyclePolicy/properties/TransitionToIA",
                ),
                Patch(
                    source=["efs", "2015-02-01"],
                    shape="PerformanceMode",
                    path="/properties/PerformanceMode",
                ),
                Patch(
                    source=["efs", "2015-02-01"],
                    shape="ThroughputMode",
                    path="/properties/ThroughputMode",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::Connection",
            patches=[
                Patch(
                    source=["glue", "2017-03-31"],
                    shape="ConnectionType",
                    path="/definitions/ConnectionInput/properties/ConnectionType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::Crawler",
            patches=[
                Patch(
                    source=["glue", "2017-03-31"],
                    shape="DeleteBehavior",
                    path="/definitions/SchemaChangePolicy/properties/DeleteBehavior",
                ),
                Patch(
                    source=["glue", "2017-03-31"],
                    shape="UpdateBehavior",
                    path="/definitions/SchemaChangePolicy/properties/UpdateBehavior",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Glue::Trigger",
            patches=[
                Patch(
                    source=["glue", "2017-03-31"],
                    shape="Logical",
                    path="/definitions/Predicate/properties/Logical",
                ),
                Patch(
                    source=["glue", "2017-03-31"],
                    shape="LogicalOperator",
                    path="/definitions/Condition/properties/LogicalOperator",
                ),
                Patch(
                    source=["glue", "2017-03-31"],
                    shape="TriggerType",
                    path="/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::GuardDuty::Detector",
            patches=[
                Patch(
                    source=["guardduty", "2017-11-28"],
                    shape="FindingPublishingFrequency",
                    path="/properties/FindingPublishingFrequency",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::GuardDuty::Filter",
            patches=[
                Patch(
                    source=["guardduty", "2017-11-28"],
                    shape="FilterAction",
                    path="/properties/Action",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::GuardDuty::IPSet",
            patches=[
                Patch(
                    source=["guardduty", "2017-11-28"],
                    shape="IpSetFormat",
                    path="/properties/Format",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::GuardDuty::ThreatIntelSet",
            patches=[
                Patch(
                    source=["guardduty", "2017-11-28"],
                    shape="ThreatIntelSetFormat",
                    path="/properties/Format",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::IAM::AccessKey",
            patches=[
                Patch(
                    source=["iam", "2010-05-08"],
                    shape="statusType",
                    path="/properties/Status",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::KinesisAnalyticsV2::Application",
            patches=[
                Patch(
                    source=["kinesisanalyticsv2", "2018-05-23"],
                    shape="RuntimeEnvironment",
                    path="/properties/RuntimeEnvironment",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Lambda::Function",
            patches=[
                Patch(
                    source=["lambda", "2015-03-31"],
                    shape="Runtime",
                    path="/properties/Runtime",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Lambda::EventSourceMapping",
            patches=[
                Patch(
                    source=["lambda", "2015-03-31"],
                    shape="EventSourcePosition",
                    path="/properties/StartingPosition",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::OpsWorks::Instance",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="VolumeType",
                    path="/definitions/EbsBlockDevice/properties/VolumeType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::OpsWorks::Layer",
            patches=[
                Patch(
                    source=["ec2", "2016-11-15"],
                    shape="VolumeType",
                    path="/definitions/VolumeConfiguration/properties/VolumeType",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Route53::RecordSetGroup",
            patches=[
                Patch(
                    source=["route53", "2013-04-01"],
                    shape="ResourceRecordSetFailover",
                    path="/definitions/RecordSet/properties/Failover",
                ),
                Patch(
                    source=["route53", "2013-04-01"],
                    shape="RRType",
                    path="/definitions/RecordSet/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::Route53Resolver::ResolverEndpoint",
            patches=[
                Patch(
                    source=["route53resolver", "2018-04-01"],
                    shape="ResolverEndpointDirection",
                    path="/properties/Direction",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::ServiceDiscovery::Service",
            patches=[
                Patch(
                    source=["servicediscovery", "2017-03-14"],
                    shape="RecordType",
                    path="/definitions/DnsRecord/properties/Type",
                ),
                Patch(
                    source=["servicediscovery", "2017-03-14"],
                    shape="HealthCheckType",
                    path="/definitions/HealthCheckConfig/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::SES::ReceiptRule",
            patches=[
                Patch(
                    source=["ses", "2010-12-01"],
                    shape="TlsPolicy",
                    path="/definitions/Rule/properties/TlsPolicy",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::WAFRegional::Rule",
            patches=[
                Patch(
                    source=["waf", "2015-08-24"],
                    shape="PredicateType",
                    path="/definitions/Predicate/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::WAF::Rule",
            patches=[
                Patch(
                    source=["waf", "2015-08-24"],
                    shape="PredicateType",
                    path="/definitions/Predicate/properties/Type",
                ),
            ],
        ),
        ResourcePatch(
            resource_type="AWS::WorkSpaces::Workspace",
            patches=[
                Patch(
                    source=["workspaces", "2015-04-08"],
                    shape="RunningMode",
                    path="/definitions/WorkspaceProperties/properties/RunningMode",
                ),
                Patch(
                    source=["workspaces", "2015-04-08"],
                    shape="Compute",
                    path="/definitions/WorkspaceProperties/properties/ComputeTypeName",
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


def build_resource_type_patches(dir: str, resource_patches: ResourcePatch):
    LOGGER.info(f"Applying patches for {resource_patches.resource_type}")

    resource_name = resource_patches.resource_type.lower().replace("::", "_")
    output_dir = os.path.join("src/cfnlint/data/schemas/patches/extensions/all/")
    output_file = os.path.join(
        output_dir,
        resource_name,
        "boto.json",
    )

    with open(output_file, "w+") as fh:
        d = []
        boto_d = {}
        for patch in resource_patches.patches:
            enums = []
            service_path = (
                ["botocore-master/botocore/data"] + patch.source + ["service-2.json"]
            )
            with open(os.path.join(dir, *service_path), "r") as f:
                boto_d = json.load(f)

            enums = boto_d.get("shapes").get(patch.shape).get("enum")  # type: ignore
            d.append(
                {
                    "op": "add",
                    "path": f"{patch.path}/enum",
                    "value": enums,
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


def build_patches(dir: str):
    for patch in patches:
        build_resource_type_patches(dir, resource_patches=patch)


def main():
    """main function"""
    configure_logging()
    with tempfile.TemporaryDirectory() as dir:
        r = requests.get(BOTO_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(dir)

        build_patches(dir)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
