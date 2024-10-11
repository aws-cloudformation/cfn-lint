"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from _types import AllPatches, Patch

patches: AllPatches = {
    "AWS::AmazonMQ::Broker": {
        "/properties/AuthenticationStrategy": Patch(
            source=["mq", "2017-11-27"],
            shape="AuthenticationStrategy",
        ),
        "/properties/DataReplicationMode": Patch(
            source=["mq", "2017-11-27"],
            shape="DataReplicationMode",
        ),
        "/properties/DeploymentMode": Patch(
            source=["mq", "2017-11-27"],
            shape="DeploymentMode",
        ),
        "/properties/EngineType": Patch(
            source=["mq", "2017-11-27"],
            shape="EngineType",
        ),
        "/properties/StorageType": Patch(
            source=["mq", "2017-11-27"],
            shape="BrokerStorageType",
        ),
    },
    "AWS::AmazonMQ::Configuration": {
        "/properties/AuthenticationStrategy": Patch(
            source=["mq", "2017-11-27"],
            shape="AuthenticationStrategy",
        ),
        "/properties/EngineType": Patch(
            source=["mq", "2017-11-27"],
            shape="EngineType",
        ),
    },
    "AWS::ApiGateway::RestApi": {
        "/properties/ApiKeySourceType": Patch(
            source=["apigateway", "2015-07-09"],
            shape="ApiKeySourceType",
        ),
    },
    "AWS::ApiGateway::Authorizer": {
        "/properties/Type": Patch(
            source=["apigateway", "2015-07-09"],
            shape="AuthorizerType",
        ),
    },
    "AWS::ApiGateway::GatewayResponse": {
        "/properties/ResponseType": Patch(
            source=["apigateway", "2015-07-09"],
            shape="GatewayResponseType",
        ),
    },
    "AWS::ApplicationAutoScaling::ScalingPolicy": {
        "/properties/PolicyType": Patch(
            source=["application-autoscaling", "2016-02-06"],
            shape="PolicyType",
        ),
        "/definitions/PredefinedMetricSpecification/properties/PredefinedMetricType": Patch(
            source=["application-autoscaling", "2016-02-06"],
            shape="MetricType",
        ),
    },
    "AWS::AppSync::DataSource": {
        "/properties/Type": Patch(
            source=["appsync", "2017-07-25"],
            shape="DataSourceType",
        ),
    },
    "AWS::AppSync::GraphQLApi": {
        "/properties/AuthenticationType": Patch(
            source=["appsync", "2017-07-25"],
            shape="AuthenticationType",
        ),
    },
    "AWS::AppSync::Resolver": {
        "/properties/Kind": Patch(
            source=["appsync", "2017-07-25"],
            shape="ResolverKind",
        ),
    },
    "AWS::AutoScaling::LaunchConfiguration": {
        "/definitions/BlockDevice/properties/VolumeType": Patch(
            source=["ec2", "2016-11-15"],
            shape="VolumeType",
        ),
    },
    "AWS::AutoScaling::ScalingPolicy": {
        "/definitions/CustomizedMetricSpecification/properties/Statistic": Patch(
            source=["autoscaling", "2011-01-01"],
            shape="MetricStatistic",
        ),
        "/definitions/PredefinedMetricSpecification/properties/PredefinedMetricType": Patch(
            source=["autoscaling", "2011-01-01"],
            shape="MetricType",
        ),
    },
    "AWS::AutoScalingPlans::ScalingPlan": {
        "/definitions/ScalingInstruction/properties/ScalableDimension": Patch(
            source=["autoscaling-plans", "2018-01-06"],
            shape="ScalableDimension",
        ),
        "/definitions/ScalingInstruction/properties/ServiceNamespace": Patch(
            source=["autoscaling-plans", "2018-01-06"],
            shape="ServiceNamespace",
        ),
        "/definitions/ScalingInstruction/properties/PredictiveScalingMaxCapacityBehavior": Patch(
            source=["autoscaling-plans", "2018-01-06"],
            shape="PredictiveScalingMaxCapacityBehavior",
        ),
        "/definitions/ScalingInstruction/properties/PredictiveScalingMode": Patch(
            source=["autoscaling-plans", "2018-01-06"],
            shape="PredictiveScalingMode",
        ),
    },
    "AWS::Budgets::Budget": {
        "/definitions/BudgetData/properties/BudgetType": Patch(
            source=["budgets", "2016-10-20"],
            shape="BudgetType",
        ),
        "/definitions/BudgetData/properties/TimeUnit": Patch(
            source=["budgets", "2016-10-20"],
            shape="TimeUnit",
        ),
        "/definitions/Notification/properties/ComparisonOperator": Patch(
            source=["budgets", "2016-10-20"],
            shape="ComparisonOperator",
        ),
        "/definitions/Notification/properties/NotificationType": Patch(
            source=["budgets", "2016-10-20"],
            shape="NotificationType",
        ),
        "/definitions/Notification/properties/ThresholdType": Patch(
            source=["budgets", "2016-10-20"],
            shape="ThresholdType",
        ),
        "/definitions/Subscriber/properties/SubscriptionType": Patch(
            source=["budgets", "2016-10-20"],
            shape="SubscriptionType",
        ),
    },
    "AWS::CertificateManager::Certificate": {
        "/properties/ValidationMethod": Patch(
            source=["acm", "2015-12-08"],
            shape="ValidationMethod",
        ),
    },
    "AWS::CloudFormation::StackSet": {
        "/properties/PermissionModel": Patch(
            source=["cloudformation", "2010-05-15"],
            shape="PermissionModels",
        ),
    },
    "AWS::CloudFront::Distribution": {
        "/definitions/CacheBehavior/properties/ViewerProtocolPolicy": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="ViewerProtocolPolicy",
        ),
        "/definitions/GeoRestriction/properties/RestrictionType": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="GeoRestrictionType",
        ),
        "/definitions/DistributionConfig/properties/HttpVersion": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="HttpVersion",
        ),
        "/definitions/FunctionAssociation/properties/EventType": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="EventType",
        ),
        "/definitions/LegacyCustomOrigin/properties/OriginProtocolPolicy": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="OriginProtocolPolicy",
        ),
        "/definitions/CustomOriginConfig/properties/OriginSSLProtocols/items": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="SslProtocol",
        ),
        "/definitions/LegacyCustomOrigin/properties/OriginSSLProtocols/items": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="SslProtocol",
        ),
        "/definitions/DistributionConfig/properties/PriceClass": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="PriceClass",
        ),
        "/definitions/ViewerCertificate/properties/MinimumProtocolVersion": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="MinimumProtocolVersion",
        ),
        "/definitions/ViewerCertificate/properties/SslSupportMethod": Patch(
            source=["cloudfront", "2020-05-31"],
            shape="SSLSupportMethod",
        ),
    },
    "AWS::CloudWatch::Alarm": {
        "/properties/ComparisonOperator": Patch(
            source=["cloudwatch", "2010-08-01"],
            shape="ComparisonOperator",
        ),
        "/properties/Statistic": Patch(
            source=["cloudwatch", "2010-08-01"],
            shape="Statistic",
        ),
        "/properties/Unit": Patch(
            source=["cloudwatch", "2010-08-01"],
            shape="StandardUnit",
        ),
    },
    "AWS::CodeBuild::Project": {
        "/definitions/Artifacts/properties/Packaging": Patch(
            source=["codebuild", "2016-10-06"],
            shape="ArtifactPackaging",
        ),
        "/definitions/Artifacts/properties/Type": Patch(
            source=["codebuild", "2016-10-06"],
            shape="ArtifactsType",
        ),
        "/definitions/Environment/properties/ComputeType": Patch(
            source=["codebuild", "2016-10-06"],
            shape="ComputeType",
        ),
        "/definitions/Environment/properties/ImagePullCredentialsType": Patch(
            source=["codebuild", "2016-10-06"],
            shape="ImagePullCredentialsType",
        ),
        "/definitions/Environment/properties/Type": Patch(
            source=["codebuild", "2016-10-06"],
            shape="EnvironmentType",
        ),
        "/definitions/ProjectCache/properties/Type": Patch(
            source=["codebuild", "2016-10-06"],
            shape="CacheType",
        ),
        "/definitions/Source/properties/Type": Patch(
            source=["codebuild", "2016-10-06"],
            shape="SourceType",
        ),
    },
    "AWS::CodeCommit::Repository": {
        "/definitions/RepositoryTrigger/properties/Events/items": Patch(
            source=["codecommit", "2015-04-13"],
            shape="RepositoryTriggerEventEnum",
        ),
    },
    "AWS::CodeDeploy::Application": {
        "/properties/ComputePlatform": Patch(
            source=["codedeploy", "2014-10-06"],
            shape="ComputePlatform",
        ),
    },
    "AWS::CodeDeploy::DeploymentGroup": {
        "/definitions/AutoRollbackConfiguration/properties/Events/items": Patch(
            source=["codedeploy", "2014-10-06"],
            shape="AutoRollbackEvent",
        ),
        "/definitions/DeploymentStyle/properties/DeploymentOption": Patch(
            source=["codedeploy", "2014-10-06"],
            shape="DeploymentOption",
        ),
        "/definitions/DeploymentStyle/properties/DeploymentType": Patch(
            source=["codedeploy", "2014-10-06"],
            shape="DeploymentType",
        ),
        "/definitions/TriggerConfig/properties/TriggerEvents/items": Patch(
            source=["codedeploy", "2014-10-06"],
            shape="TriggerEventType",
        ),
    },
    "AWS::CodeDeploy::DeploymentConfig": {
        "/definitions/MinimumHealthyHosts/properties/Type": Patch(
            source=["codedeploy", "2014-10-06"],
            shape="MinimumHealthyHostsType",
        ),
    },
    "AWS::CodePipeline::Pipeline": {
        "/definitions/ActionTypeId/properties/Category": Patch(
            source=["codepipeline", "2015-07-09"],
            shape="ActionCategory",
        ),
        "/definitions/ActionTypeId/properties/Owner": Patch(
            source=["codepipeline", "2015-07-09"],
            shape="ActionOwner",
        ),
        "/definitions/ArtifactStore/properties/Type": Patch(
            source=["codepipeline", "2015-07-09"],
            shape="ArtifactStoreType",
        ),
        "/definitions/BlockerDeclaration/properties/Type": Patch(
            source=["codepipeline", "2015-07-09"],
            shape="BlockerType",
        ),
    },
    "AWS::CodePipeline::CustomActionType": {
        "/definitions/ConfigurationProperties/properties/Type": Patch(
            source=["codepipeline", "2015-07-09"],
            shape="ActionConfigurationPropertyType",
        ),
    },
    "AWS::CodePipeline::Webhook": {
        "/properties/Authentication": Patch(
            source=["codepipeline", "2015-07-09"],
            shape="WebhookAuthenticationType",
        ),
    },
    "AWS::Cognito::UserPool": {
        "/properties/AliasAttributes/items": Patch(
            source=["cognito-idp", "2016-04-18"],
            shape="AliasAttributeType",
        ),
        "/properties/UsernameAttributes/items": Patch(
            source=["cognito-idp", "2016-04-18"],
            shape="UsernameAttributeType",
        ),
        "/properties/MfaConfiguration": Patch(
            source=["cognito-idp", "2016-04-18"],
            shape="UserPoolMfaType",
        ),
    },
    "AWS::Cognito::UserPoolUser": {
        "/properties/DesiredDeliveryMediums/items": Patch(
            source=["cognito-idp", "2016-04-18"],
            shape="DeliveryMediumType",
        ),
        "/properties/MessageAction": Patch(
            source=["cognito-idp", "2016-04-18"],
            shape="MessageActionType",
        ),
    },
    "AWS::Cognito::UserPoolClient": {
        "/properties/ExplicitAuthFlows/items": Patch(
            source=["cognito-idp", "2016-04-18"],
            shape="ExplicitAuthFlowsType",
        ),
    },
    "AWS::Config::ConfigRule": {
        "/definitions/Source/properties/Owner": Patch(
            source=["config", "2014-11-12"],
            shape="Owner",
        ),
        "/definitions/SourceDetail/properties/EventSource": Patch(
            source=["config", "2014-11-12"],
            shape="EventSource",
        ),
        "/definitions/SourceDetail/properties/MaximumExecutionFrequency": Patch(
            source=["config", "2014-11-12"],
            shape="MaximumExecutionFrequency",
        ),
        "/definitions/SourceDetail/properties/MessageType": Patch(
            source=["config", "2014-11-12"],
            shape="MessageType",
        ),
    },
    "AWS::DirectoryService::MicrosoftAD": {
        "/properties/Edition": Patch(
            source=["ds", "2015-04-16"],
            shape="DirectoryEdition",
        ),
    },
    "AWS::DirectoryService::SimpleAD": {
        "/properties/Size": Patch(
            source=["ds", "2015-04-16"],
            shape="DirectorySize",
        )
    },
    "AWS::DLM::LifecyclePolicy": {
        "/definitions/PolicyDetails/properties/ResourceTypes/items": Patch(
            source=["dlm", "2018-01-12"],
            shape="ResourceTypeValues",
        ),
    },
    "AWS::DMS::Endpoint": {
        "/properties/SslMode": Patch(
            source=["dms", "2016-01-01"],
            shape="DmsSslModeValue",
        ),
        "/properties/EndpointType": Patch(
            source=["dms", "2016-01-01"],
            shape="ReplicationEndpointTypeValue",
        ),
    },
    "AWS::DynamoDB::Table": {
        "/definitions/AttributeDefinition/properties/AttributeType": Patch(
            source=["dynamodb", "2012-08-10"],
            shape="ScalarAttributeType",
        ),
        "/properties/BillingMode": Patch(
            source=["dynamodb", "2012-08-10"],
            shape="BillingMode",
        ),
        "/definitions/KeySchema/properties/KeyType": Patch(
            source=["dynamodb", "2012-08-10"],
            shape="KeyType",
        ),
        "/definitions/Projection/properties/ProjectionType": Patch(
            source=["dynamodb", "2012-08-10"],
            shape="ProjectionType",
        ),
        "/definitions/StreamSpecification/properties/StreamViewType": Patch(
            source=["dynamodb", "2012-08-10"],
            shape="StreamViewType",
        ),
    },
    "AWS::EC2::CapacityReservation": {
        "/properties/EndDateType": Patch(
            source=["ec2", "2016-11-15"],
            shape="EndDateType",
        ),
        "/properties/InstanceMatchCriteria": Patch(
            source=["ec2", "2016-11-15"],
            shape="InstanceMatchCriteria",
        ),
        "/properties/InstancePlatform": Patch(
            source=["ec2", "2016-11-15"],
            shape="CapacityReservationInstancePlatform",
        ),
    },
    "AWS::EC2::CustomerGateway": {
        "/properties/Type": Patch(
            source=["ec2", "2016-11-15"],
            shape="GatewayType",
        ),
    },
    "AWS::EC2::EIP": {
        "/properties/Domain": Patch(
            source=["ec2", "2016-11-15"],
            shape="DomainType",
        ),
    },
    "AWS::EC2::EC2Fleet": {
        "/definitions/OnDemandOptionsRequest/properties/AllocationStrategy": Patch(
            source=["ec2", "2016-11-15"],
            shape="FleetOnDemandAllocationStrategy",
        ),
    },
    "AWS::EC2::Host": {
        "/properties/AutoPlacement": Patch(
            source=["ec2", "2016-11-15"],
            shape="AutoPlacement",
        ),
    },
    "AWS::EC2::Instance": {
        "/properties/Affinity": Patch(
            source=["ec2", "2016-11-15"],
            shape="Affinity",
        ),
        "/properties/Tenancy": Patch(
            source=["ec2", "2016-11-15"],
            shape="Tenancy",
        ),
    },
    "AWS::EC2::LaunchTemplate": {
        "/definitions/LaunchTemplateData/properties/InstanceInitiatedShutdownBehavior": Patch(
            source=["ec2", "2016-11-15"],
            shape="ShutdownBehavior",
        ),
        "/definitions/InstanceMarketOptions/properties/MarketType": Patch(
            source=["ec2", "2016-11-15"],
            shape="MarketType",
        ),
        "/definitions/SpotOptions/properties/InstanceInterruptionBehavior": Patch(
            source=["ec2", "2016-11-15"],
            shape="SpotInstanceInterruptionBehavior",
        ),
        "/definitions/SpotOptions/properties/SpotInstanceType": Patch(
            source=["ec2", "2016-11-15"],
            shape="SpotInstanceType",
        ),
        "/definitions/Ebs/properties/VolumeType": Patch(
            source=["ec2", "2016-11-15"],
            shape="VolumeType",
        ),
        "/definitions/Placement/properties/Tenancy": Patch(
            source=["ec2", "2016-11-15"],
            shape="Tenancy",
        ),
        "/definitions/TagSpecification/properties/ResourceType": Patch(
            source=["ec2", "2016-11-15"],
            shape="ResourceType",
        ),
    },
    "AWS::EC2::NetworkAclEntry": {
        "/properties/RuleAction": Patch(
            source=["ec2", "2016-11-15"],
            shape="RuleAction",
        ),
    },
    "AWS::EC2::NetworkInterfacePermission": {
        "/properties/Permission": Patch(
            source=["ec2", "2016-11-15"],
            shape="InterfacePermissionType",
        ),
    },
    "AWS::EC2::PlacementGroup": {
        "/properties/Strategy": Patch(
            source=["ec2", "2016-11-15"],
            shape="PlacementGroupStrategy",
        ),
    },
    "AWS::EC2::SpotFleet": {
        "/definitions/EbsBlockDevice/properties/VolumeType": Patch(
            source=["ec2", "2016-11-15"],
            shape="VolumeType",
        ),
    },
    "AWS::ECS::TaskDefinition": {
        "/properties/NetworkMode": Patch(
            source=["ecs", "2014-11-13"],
            shape="NetworkMode",
        ),
        "/definitions/ProxyConfiguration/properties/Type": Patch(
            source=["ecs", "2014-11-13"],
            shape="ProxyConfigurationType",
        ),
    },
    "AWS::EFS::FileSystem": {
        "/definitions/LifecyclePolicy/properties/TransitionToIA": Patch(
            source=["efs", "2015-02-01"],
            shape="TransitionToIARules",
        ),
        "/properties/PerformanceMode": Patch(
            source=["efs", "2015-02-01"],
            shape="PerformanceMode",
        ),
        "/properties/ThroughputMode": Patch(
            source=["efs", "2015-02-01"],
            shape="ThroughputMode",
        ),
    },
    "AWS::Glue::Connection": {
        "/definitions/ConnectionInput/properties/ConnectionType": Patch(
            source=["glue", "2017-03-31"],
            shape="ConnectionType",
        ),
    },
    "AWS::Glue::Crawler": {
        "/definitions/SchemaChangePolicy/properties/DeleteBehavior": Patch(
            source=["glue", "2017-03-31"],
            shape="DeleteBehavior",
        ),
        "/definitions/SchemaChangePolicy/properties/UpdateBehavior": Patch(
            source=["glue", "2017-03-31"],
            shape="UpdateBehavior",
        ),
    },
    "AWS::Glue::Trigger": {
        "/definitions/Predicate/properties/Logical": Patch(
            source=["glue", "2017-03-31"],
            shape="Logical",
        ),
        "/definitions/Condition/properties/LogicalOperator": Patch(
            source=["glue", "2017-03-31"],
            shape="LogicalOperator",
        ),
        "/properties/Type": Patch(
            source=["glue", "2017-03-31"],
            shape="TriggerType",
        ),
    },
    "AWS::GuardDuty::Detector": {
        "/properties/FindingPublishingFrequency": Patch(
            source=["guardduty", "2017-11-28"],
            shape="FindingPublishingFrequency",
        ),
    },
    "AWS::GuardDuty::Filter": {
        "/properties/Action": Patch(
            source=["guardduty", "2017-11-28"],
            shape="FilterAction",
        ),
    },
    "AWS::GuardDuty::IPSet": {
        "/properties/Format": Patch(
            source=["guardduty", "2017-11-28"],
            shape="IpSetFormat",
        ),
    },
    "AWS::GuardDuty::ThreatIntelSet": {
        "/properties/Format": Patch(
            source=["guardduty", "2017-11-28"],
            shape="ThreatIntelSetFormat",
        ),
    },
    "AWS::IAM::AccessKey": {
        "/properties/Status": Patch(
            source=["iam", "2010-05-08"],
            shape="statusType",
        ),
    },
    "AWS::KinesisAnalyticsV2::Application": {
        "/properties/RuntimeEnvironment": Patch(
            source=["kinesisanalyticsv2", "2018-05-23"],
            shape="RuntimeEnvironment",
        ),
    },
    "AWS::Lambda::Function": {
        "/properties/Runtime": Patch(
            source=["lambda", "2015-03-31"],
            shape="Runtime",
        ),
    },
    "AWS::Lambda::EventSourceMapping": {
        "/properties/StartingPosition": Patch(
            source=["lambda", "2015-03-31"],
            shape="EventSourcePosition",
        ),
    },
    "AWS::OpsWorks::Instance": {
        "/definitions/EbsBlockDevice/properties/VolumeType": Patch(
            source=["ec2", "2016-11-15"],
            shape="VolumeType",
        ),
    },
    "AWS::OpsWorks::Layer": {
        "/definitions/VolumeConfiguration/properties/VolumeType": Patch(
            source=["ec2", "2016-11-15"],
            shape="VolumeType",
        ),
    },
    "AWS::Route53::RecordSetGroup": {
        "/definitions/RecordSet/properties/Failover": Patch(
            source=["route53", "2013-04-01"],
            shape="ResourceRecordSetFailover",
        ),
        "/definitions/RecordSet/properties/Type": Patch(
            source=["route53", "2013-04-01"],
            shape="RRType",
        ),
    },
    "AWS::Route53Resolver::ResolverEndpoint": {
        "/properties/Direction": Patch(
            source=["route53resolver", "2018-04-01"],
            shape="ResolverEndpointDirection",
        ),
    },
    "AWS::ServiceDiscovery::Service": {
        "/definitions/DnsRecord/properties/Type": Patch(
            source=["servicediscovery", "2017-03-14"],
            shape="RecordType",
        ),
        "/definitions/HealthCheckConfig/properties/Type": Patch(
            source=["servicediscovery", "2017-03-14"],
            shape="HealthCheckType",
        ),
    },
    "AWS::SES::ReceiptRule": {
        "/definitions/Rule/properties/TlsPolicy": Patch(
            source=["ses", "2010-12-01"],
            shape="TlsPolicy",
        ),
    },
    "AWS::WAFRegional::Rule": {
        "/definitions/Predicate/properties/Type": Patch(
            source=["waf", "2015-08-24"],
            shape="PredicateType",
        ),
    },
    "AWS::WorkSpaces::Workspace": {
        "/definitions/WorkspaceProperties/properties/RunningMode": Patch(
            source=["workspaces", "2015-04-08"],
            shape="RunningMode",
        ),
        "/definitions/WorkspaceProperties/properties/ComputeTypeName": Patch(
            source=["workspaces", "2015-04-08"],
            shape="Compute",
        ),
    },
}
