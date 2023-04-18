#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

"""
    Updates our patches from boto enums
"""
from typing import List, Dict
import json
import logging
import tempfile
import zipfile
import requests
import io
import os
from collections import namedtuple

LOGGER = logging.getLogger("cfnlint")

BOTO_URL = "https://github.com/boto/botocore/archive/refs/heads/master.zip"

patch = namedtuple("Patch", ["source", "shape", "path"])
resource_patch = namedtuple("ResourcePatch", ["resource_type", "patches"])
patches: List[resource_patch] = []
patches.extend(
    [
        resource_patch(
            resource_type="AWS::AmazonMQ::Broker",
            patches=[
                patch(
                    source=["mq", "2017-11-27"],
                    shape="DeploymentMode",
                    path="/properties/DeploymentMode",
                ),
                patch(
                    source=["mq", "2017-11-27"],
                    shape="EngineType",
                    path="/properties/EngineType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ApiGateway::RestApi",
            patches=[
                patch(
                    source=["apigateway", "2015-07-09"],
                    shape="ApiKeySourceType",
                    path="/properties/ApiKeySourceType",
                ),
                patch(
                    source=["apigateway", "2015-07-09"],
                    shape="GatewayResponseType",
                    path="/properties/GatewayResponseType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ApiGateway::Authorizer",
            patches=[
                patch(
                    source=["apigateway", "2015-07-09"],
                    shape="AuthorizerType",
                    path="/properties/Type",
                ),
                patch(
                    source=["apigateway", "2015-07-09"],
                    shape="GatewayResponseType",
                    path="/properties/GatewayResponseType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ApiGateway::GatewayResponse",
            patches=[
                patch(
                    source=["apigateway", "2015-07-09"],
                    shape="GatewayResponseType",
                    path="/properties/ResponseType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::ApplicationAutoScaling::ScalingPolicy",
            patches=[
                patch(
                    source=["application-autoscaling", "2016-02-06"],
                    shape="PolicyType",
                    path="/properties/PolicyType",
                ),
                patch(
                    source=["application-autoscaling", "2016-02-06"],
                    shape="MetricType",
                    path="/definitions/PredefinedMetricSpecification/properties/PredefinedMetricType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AppSync::DataSource",
            patches=[
                patch(
                    source=["appsync", "2017-07-25"],
                    shape="DataSourceType",
                    path="/properties/Type",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AppSync::GraphQLApi",
            patches=[
                patch(
                    source=["appsync", "2017-07-25"],
                    shape="AuthenticationType",
                    path="/properties/AuthenticationType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AppSync::Resolver",
            patches=[
                patch(
                    source=["appsync", "2017-07-25"],
                    shape="ResolverKind",
                    path="/properties/Kind",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AutoScaling::ScalingPolicy",
            patches=[
                patch(
                    source=["autoscaling", "2011-01-01"],
                    shape="MetricStatistic",
                    path="/definitions/CustomizedMetricSpecification/properties/Statistic",
                ),
                patch(
                    source=["autoscaling", "2011-01-01"],
                    shape="MetricType",
                    path="/definitions/PredefinedMetricSpecification/properties/PredefinedMetricType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::AutoScalingPlans::ScalingPlan",
            patches=[
                patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="ScalableDimension",
                    path="/definitions/ScalingInstruction/properties/ScalableDimension",
                ),
                patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="ServiceNamespace",
                    path="/definitions/ScalingInstruction/properties/ServiceNamespace",
                ),
                patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="PredictiveScalingMaxCapacityBehavior",
                    path="/definitions/ScalingInstruction/properties/PredictiveScalingMaxCapacityBehavior",
                ),
                patch(
                    source=["autoscaling-plans", "2018-01-06"],
                    shape="PredictiveScalingMode",
                    path="/definitions/ScalingInstruction/properties/PredictiveScalingMode",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Budgets::Budget",
            patches=[
                patch(
                    source=["budgets", "2016-10-20"],
                    shape="BudgetType",
                    path="/definitions/BudgetData/properties/BudgetType",
                ),
                patch(
                    source=["budgets", "2016-10-20"],
                    shape="TimeUnit",
                    path="/definitions/BudgetData/properties/TimeUnit",
                ),
                patch(
                    source=["budgets", "2016-10-20"],
                    shape="ComparisonOperator",
                    path="/definitions/Notification/properties/ComparisonOperator",
                ),
                patch(
                    source=["budgets", "2016-10-20"],
                    shape="NotificationType",
                    path="/definitions/Notification/properties/NotificationType",
                ),
                patch(
                    source=["budgets", "2016-10-20"],
                    shape="ThresholdType",
                    path="/definitions/Notification/properties/ThresholdType",
                ),
                patch(
                    source=["budgets", "2016-10-20"],
                    shape="SubscriptionType",
                    path="/definitions/Subscriber/properties/SubscriptionType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CloudFormation::StackSet",
            patches=[
                patch(
                    source=["cloudformation", "2010-05-15"],
                    shape="PermissionModels",
                    path="/properties/PermissionModel",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CloudFront::Distribution",
            patches=[
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="ViewerProtocolPolicy",
                    path="/definitions/CacheBehavior/properties/ViewerProtocolPolicy",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="GeoRestrictionType",
                    path="/definitions/GeoRestriction/properties/RestrictionType",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="HttpVersion",
                    path="/definitions/DistributionConfig/properties/HttpVersion",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="EventType",
                    path="/definitions/FunctionAssociation/properties/EventType",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="OriginProtocolPolicy",
                    path="/definitions/LegacyCustomOrigin/properties/OriginProtocolPolicy",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="SslProtocol",
                    path="/definitions/CustomOriginConfig/properties/OriginSSLProtocols/items",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="SslProtocol",
                    path="/definitions/LegacyCustomOrigin/properties/OriginSSLProtocols/items",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="PriceClass",
                    path="/definitions/DistributionConfig/properties/PriceClass",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="MinimumProtocolVersion",
                    path="/definitions/ViewerCertificate/properties/MinimumProtocolVersion",
                ),
                patch(
                    source=["cloudfront", "2020-05-31"],
                    shape="SSLSupportMethod",
                    path="/definitions/ViewerCertificate/properties/SSLSupportMethod",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CloudWatch::Alarm",
            patches=[
                patch(
                    source=["cloudwatch", "2010-08-01"],
                    shape="ComparisonOperator",
                    path="/properties/ComparisonOperator",
                ),
                patch(
                    source=["cloudwatch", "2010-08-01"],
                    shape="Statistic",
                    path="/properties/Statistic",
                ),
                patch(
                    source=["cloudwatch", "2010-08-01"],
                    shape="StandardUnit",
                    path="/properties/Unit",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeBuild::Project",
            patches=[
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ArtifactPackaging",
                    path="/definitions/Artifact/properties/Packaging",
                ),
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ArtifactsType",
                    path="/definitions/Artifact/properties/Type",
                ),
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ComputeType",
                    path="/definitions/Environment/properties/ComputeType",
                ),
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="ImagePullCredentialsType",
                    path="/definitions/Environment/properties/ImagePullCredentialsType",
                ),
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="EnvironmentType",
                    path="/definitions/Environment/properties/Type",
                ),
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="CacheType",
                    path="/definitions/ProjectCache/properties/Type",
                ),
                patch(
                    source=["codebuild", "2016-10-06"],
                    shape="SourceType",
                    path="/definitions/Source/properties/Type",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                patch(
                    source=["codecommit", "2015-04-13"],
                    shape="RepositoryTriggerEventEnum",
                    path="/definitions/RepositoryTrigger/properties/Events/items",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeCommit::Repository",
            patches=[
                patch(
                    source=["codecommit", "2015-04-13"],
                    shape="RepositoryTriggerEventEnum",
                    path="/definitions/RepositoryTrigger/properties/Events/items",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeDeploy::Application",
            patches=[
                patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="ComputePlatform",
                    path="/properties/ComputePlatform",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeDeploy::DeploymentGroup",
            patches=[
                patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="AutoRollbackEvent",
                    path="/properties/AutoRollbackConfiguration/properties/Events/items",
                ),
                patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="DeploymentOption",
                    path="/properties/DeploymentStyle/properties/DeploymentOption",
                ),
                patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="DeploymentType",
                    path="/properties/DeploymentStyle/properties/DeploymentType",
                ),
                patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="TriggerEventType",
                    path="/properties/TriggerConfig/properties/TriggerEvents",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodeDeploy::DeploymentConfig",
            patches=[
                patch(
                    source=["codedeploy", "2014-10-06"],
                    shape="MinimumHealthyHostsType",
                    path="/definitions/MinimumHealthyHosts/properties/Type",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodePipeline::Pipeline",
            patches=[
                patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ActionCategory",
                    path="/definitions/ActionTypeId/properties/Category",
                ),
                patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ActionOwner",
                    path="/definitions/ActionTypeId/properties/Owner",
                ),
                patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ArtifactStoreType",
                    path="/definitions/ArtifactStore/properties/Type",
                ),
                patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="BlockerType",
                    path="/definitions/BlockerDeclaration/properties/Type",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodePipeline::CustomActionType",
            patches=[
                patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="ActionConfigurationPropertyType",
                    path="/definitions/ConfigurationProperties/properties/Type",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::CodePipeline::Webhook",
            patches=[
                patch(
                    source=["codepipeline", "2015-07-09"],
                    shape="WebhookAuthenticationType",
                    path="/properties/Authentication",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Cognito::UserPool",
            patches=[
                patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="AliasAttributeType",
                    path="/properties/AliasAttributes/items",
                ),
                patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="UsernameAttributeType",
                    path="/properties/UsernameAttributes/items",
                ),
                patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="UserPoolMfaType",
                    path="/properties/MfaConfiguration",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Cognito::UserPoolUser",
            patches=[
                patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="DeliveryMediumType",
                    path="/properties/DesiredDeliveryMediums/items",
                ),
                patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="MessageActionType",
                    path="/properties/MessageAction/items",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Cognito::UserPoolClient",
            patches=[
                patch(
                    source=["cognito-idp", "2016-04-18"],
                    shape="ExplicitAuthFlowsType",
                    path="/properties/ExplicitAuthFlows/items",
                )
            ],
        ),
        resource_patch(
            resource_type="AWS::Config::ConfigRule",
            patches=[
                patch(
                    source=["config", "2014-11-12"],
                    shape="Owner",
                    path="/definitions/Source/properties/Owner",
                ),
                patch(
                    source=["config", "2014-11-12"],
                    shape="EventSource",
                    path="/definitions/SourceDetail/properties/EventSource",
                ),
                patch(
                    source=["config", "2014-11-12"],
                    shape="MaximumExecutionFrequency",
                    path="/properties/SourceDetail/properties/MaximumExecutionFrequency",
                ),
                patch(
                    source=["config", "2014-11-12"],
                    shape="MessageType",
                    path="/properties/SourceDetail/properties/MessageType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::DynamoDB::Table",
            patches=[
                patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="ScalarAttributeType",
                    path="/definitions/AttributeDefinition/properties/AttributeType",
                ),
                patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="BillingMode",
                    path="/properties/BillingMode",
                ),
                patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="KeyType",
                    path="/definitions/KeySchema/properties/KeyType",
                ),
                patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="ProjectionType",
                    path="/definitions/Projection/properties/ProjectionType",
                ),
                patch(
                    source=["dynamodb", "2012-08-10"],
                    shape="StreamViewType",
                    path="/definitions/StreamSpecification/properties/StreamViewType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::EC2::Instance",
            patches=[
                patch(
                    source=["ec2", "2016-11-15"],
                    shape="Affinity",
                    path="/properties/Affinity",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::Connection",
            patches=[
                patch(
                    source=["glue", "2017-03-31"],
                    shape="ConnectionType",
                    path="/definitions/ConnectionInput/properties/ConnectionType",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::Crawler",
            patches=[
                patch(
                    source=["glue", "2017-03-31"],
                    shape="DeleteBehavior",
                    path="/definitions/SchemaChangePolicy/properties/DeleteBehavior",
                ),
                patch(
                    source=["glue", "2017-03-31"],
                    shape="UpdateBehavior",
                    path="/definitions/SchemaChangePolicy/properties/UpdateBehavior",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Glue::Trigger",
            patches=[
                patch(
                    source=["glue", "2017-03-31"],
                    shape="Logical",
                    path="/definitions/Predicate/properties/Logical",
                ),
                patch(
                    source=["glue", "2017-03-31"],
                    shape="LogicalOperator",
                    path="/definitions/Condition/properties/LogicalOperator",
                ),
                patch(
                    source=["glue", "2017-03-31"],
                    shape="TriggerType",
                    path="/properties/Type",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::GuardDuty::Detector",
            patches=[
                patch(
                    source=["guardduty", "2017-11-28"],
                    shape="FindingPublishingFrequency",
                    path="/properties/FindingPublishingFrequency",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::GuardDuty::Filter",
            patches=[
                patch(
                    source=["guardduty", "2017-11-28"],
                    shape="FilterAction",
                    path="/properties/Action",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::GuardDuty::IPSet",
            patches=[
                patch(
                    source=["guardduty", "2017-11-28"],
                    shape="IpSetFormat",
                    path="/properties/Format",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::GuardDuty::ThreatIntelSet",
            patches=[
                patch(
                    source=["guardduty", "2017-11-28"],
                    shape="ThreatIntelSetFormat",
                    path="/properties/Format",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::IAM::AccessKey",
            patches=[
                patch(
                    source=["iam", "2010-05-08"],
                    shape="statusType",
                    path="/properties/Active",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::KinesisAnalyticsV2::Application",
            patches=[
                patch(
                    source=["kinesisanalyticsv2", "2018-05-23"],
                    shape="RuntimeEnvironment",
                    path="/properties/RuntimeEnvironment",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::Lambda::EventSourceMapping",
            patches=[
                patch(
                    source=["lambda", "2015-03-31"],
                    shape="EventSourcePosition",
                    path="/properties/StartingPosition",
                ),
            ],
        ),
        resource_patch(
            resource_type="AWS::WorkSpaces::Workspace",
            patches=[
                patch(
                    source=["workspaces", "2015-04-08"],
                    shape="RunningMode",
                    path="/properties/RunningMode",
                ),
                patch(
                    source=["workspaces", "2015-04-08"],
                    shape="Compute",
                    path="/properties/ComputeTypeName",
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


def create_output(resource_type: str, shape: str, patch: Dict[str, List[str]]):
    """update outputs with appropriate results"""
    output_dir = os.path.join("src/cfnlint/data/schemas/extensions/")
    output_file = os.path.join(
        output_dir,
        resource_type.lower().replace("::", "_"),
        f"boto_{shape.lower()}_enum.json",
    )
    with open(output_file, "w") as fh:
        json.dump(
            patch,
            fh,
            indent=1,
            separators=(",", ": "),
            sort_keys=True,
        )


def build_resource_type_patches(dir: str, resource_patches: resource_patch):
    LOGGER.info(f"Applying patches for {resource_patches.resource_type}")
    for patch in resource_patches.patches:
        service_path = (
            ["botocore-master/botocore/data"] + patch.source + ["service-2.json"]
        )
        with open(os.path.join(dir, *service_path), "r") as f:
            d = json.load(f)
            create_output(
                resource_patches.resource_type,
                patch.shape,
                {"enum": d.get("shapes").get(patch.shape).get("enum")},
            )

    resource_name = resource_patches.resource_type.lower().replace("::", "_")
    output_dir = os.path.join("src/cfnlint/data/schemas/patches/extensions/all/")
    output_file = os.path.join(
        output_dir,
        f"{resource_name}.json",
    )

    mode = 'r+' if os.path.exists(output_file) else 'w+'
    with open(output_file, mode) as fh:
        fh.seek(0)
        try:
            d = json.load(fh)
        except ValueError:
            d = []
        write_file = False
        for patch in resource_patches.patches:
            patch_path = f"{resource_name}/boto_{patch.shape.lower()}_enum"
            for d_patch in d:
                if d_patch.get("value") == patch_path:
                    break
            else:
                d.append(
                    {
                        "op": "add",
                        "path": f"{patch.path}/cfnSchema",
                        "value": patch_path,
                    }
                )
                write_file = True

        fh.seek(0)
        if write_file:
            json.dump(
                d,
                fh,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )


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
