#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import logging

import boto3

from cfnlint.helpers import REGIONS, get_url_content
from cfnlint.maintenance import SPEC_REGIONS

"""
    Updates our dynamic patches from SSM data
    This script requires Boto3 and Credentials to call the SSM API
"""

LOGGER = logging.getLogger("cfnlint")

service_map = {
    "acm": ["AWS::CertificateManager::"],
    "apigateway": ["AWS::ApiGateway::", "AWS::ApiGatewayV2::"],
    # 'application-autoscaling': ['AWS::ApplicationAutoScaling::'], ## remove because SSM endpoints aren't correct
    "appstream": ["AWS::AppStream::"],
    "appsync": ["AWS::AppSync::"],
    "athena": ["AWS::Athena::"],
    "autoscaling": ["AWS::AutoScaling::"],
    "batch": ["AWS::Batch::"],
    "budgets": ["AWS::Budgets::"],
    "cloud9": ["AWS::Cloud9::"],
    "cloudfront": ["AWS::CloudFront::"],
    "cloudtrail": ["AWS::CloudTrail::"],
    "cloudwatch": ["AWS::CloudWatch::"],
    "codebuild": ["AWS::CodeBuild::"],
    "codecommit": ["AWS::CodeCommit::"],
    "codedeploy": ["AWS::CodeDeploy::"],
    "codepipeline": ["AWS::CodePipeline::"],
    "cognito-identity": ["AWS::Cognito::"],
    "config": ["AWS::Config::"],
    "datapipeline": ["AWS::DataPipeline::"],
    "dax": ["AWS::DAX::"],
    "dms": ["AWS::DMS::"],
    "docdb": ["AWS::DocDB::"],
    "ds": ["AWS::DirectoryService::"],
    "dynamodb": ["AWS::DynamoDB::"],
    "ec2": ["AWS::EC2::"],
    "ecr": ["AWS::ECR::"],
    "ecs": ["AWS::ECS::"],
    "efs": ["AWS::EFS::"],
    "eks": ["AWS::EKS::"],
    "elasticache": ["AWS::ElastiCache::"],
    "elasticbeanstalk": ["AWS::ElasticBeanstalk::"],
    "elb": ["AWS::ElasticLoadBalancing::", "AWS::ElasticLoadBalancingV2::"],
    "emr": ["AWS::EMR::"],
    "es": ["AWS::Elasticsearch::"],
    "events": ["AWS::Events::"],
    "firehose": ["AWS::KinesisFirehose::"],
    "fsx": ["AWS::FSx::"],
    "gamelift": ["AWS::GameLift::"],
    "glue": ["AWS::Glue::"],
    "greengrass": ["AWS::Greengrass::"],
    "guardduty": ["AWS::GuardDuty::"],
    "inspector": ["AWS::Inspector::"],
    "iot": ["AWS::IoT::"],
    "iot1click-projects": ["AWS::IoT1Click::"],
    "iotanalytics": ["AWS::IoTAnalytics::"],
    "kinesis": ["AWS::Kinesis::"],
    "kinesisanalytics": ["AWS::KinesisAnalytics::", "AWS::KinesisAnalyticsV2::"],
    "kms": ["AWS::KMS::"],
    "lambda": ["AWS::Lambda::"],
    "logs": ["AWS::Logs::"],
    "mq": ["AWS::AmazonMQ::"],
    "neptune": ["AWS::Neptune::"],
    "opsworks": ["AWS::OpsWorks::"],
    "opsworkscm": ["AWS::OpsWorksCM::"],
    "ram": ["AWS::RAM::"],
    "rds": ["AWS::RDS::"],
    "redshift": ["AWS::Redshift::"],
    "robomaker": ["AWS::RoboMaker::"],
    "route53": ["AWS::Route53::"],
    "route53resolver": [
        "AWS::Route53Resolver::ResolverRule",
        "AWS::Route53Resolver::ResolverEndpoint",
    ],
    "s3": ["AWS::S3::"],
    "sagemaker": ["AWS::SageMaker::"],
    "sdb": ["AWS::SDB::"],
    "secretsmanager": ["AWS::SecretsManager::"],
    "servicecatalog": ["AWS::ServiceCatalog::"],
    "servicediscovery": ["AWS::ServiceDiscovery::"],
    "ses": ["AWS::SES::"],
    "sns": ["AWS::SNS::"],
    "sqs": ["AWS::SQS::"],
    "ssm": ["AWS::SSM::"],
    "stepfunctions": ["AWS::StepFunctions::"],
    "waf-regional": ["AWS::WAFRegional::"],
    "workspaces": ["AWS::WorkSpaces::"],
}

session = boto3.session.Session()
client = session.client("ssm", region_name="us-east-1")


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


def update_outputs(region, resource_type, name, outputs):
    """update outputs with appropriate results"""
    element = {"op": "remove", "path": "/%s/%s" % (resource_type, name)}
    outputs[region].append(element)

    return outputs


def get_regions_for_service(service):
    """get regions for a service"""
    LOGGER.info("Get the regions for service %s", service)
    results = []
    paginator = client.get_paginator("get_parameters_by_path")
    page_iterator = paginator.paginate(
        Path="/aws/service/global-infrastructure/services/{}/regions".format(service),
    )

    for page in page_iterator:
        for region in page.get("Parameters"):
            results.append(region.get("Value"))

    return results


def add_spec_patch(region, services):
    """Go through spec and determine patching"""
    LOGGER.info("Create 06_ssm_service_removal patch for region %s", region)
    spec = json.loads(get_url_content(SPEC_REGIONS.get(region)))

    patches = []

    for spec_type in ["ResourceTypes", "PropertyTypes"]:
        for resource in sorted(spec.get(spec_type).keys()):
            for service in services:
                for spec_name in service_map.get(service):
                    if resource.startswith(spec_name):
                        element = {
                            "op": "remove",
                            "path": "/%s/%s" % (spec_type, resource),
                        }
                        patches.append(element)

    filename = "src/cfnlint/data/ExtendedSpecs/%s/06_ssm_service_removal.json" % region
    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(patches, f, indent=1, sort_keys=True, separators=(",", ": "))


def add_spec_missing_services_patch(region, services):
    """Go through spec and determine patching"""
    LOGGER.info("Create 07_ssm_service_addition patch for region %s", region)
    spec_string = get_url_content(SPEC_REGIONS.get(region))
    spec_string_standard = get_url_content(SPEC_REGIONS.get("us-east-1"))

    spec = json.loads(spec_string)
    spec_standard = json.loads(spec_string_standard)

    patches = []

    for spec_type in ["ResourceTypes"]:
        for service in services:
            found = False
            for resource in sorted(spec.get(spec_type).keys()):
                for spec_name in service_map.get(service):
                    if resource.startswith(spec_name):
                        found = True
            if found is False:
                for standard_spec_type in ["ResourceTypes", "PropertyTypes"]:
                    for resource in sorted(
                        spec_standard.get(standard_spec_type).keys()
                    ):
                        for spec_name in service_map.get(service):
                            if resource.startswith(spec_name):
                                if spec_standard.get(standard_spec_type).get(resource):
                                    element = {
                                        "op": "add",
                                        "path": "/%s/%s"
                                        % (standard_spec_type, resource),
                                        "value": spec_standard.get(
                                            standard_spec_type
                                        ).get(resource),
                                    }
                                    patches.append(element)
                                elif standard_spec_type == "ResourceTypes":
                                    print("patch for %s not found" % service)

    filename = (
        "src/cfnlint/data/ExtendedSpecs/%s/07_ssm_service_addition.json" % region
    )
    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(patches, f, indent=1, sort_keys=True, separators=(",", ": "))
            


def main():
    """main function"""
    configure_logging()

    all_regions = list(set(REGIONS))
    region_service_removal_map = {}
    region_service_add_map = {}
    for region in all_regions:
        region_service_removal_map[region] = []
        region_service_add_map[region] = []
    for service in service_map:
        regions = get_regions_for_service(service)
        if regions:
            for region in list(set(regions)):
                region_service_add_map[region].append(service)
            for region in list(set(all_regions) - set(regions)):
                region_service_removal_map[region].append(service)

    for region, services in region_service_removal_map.items():
        if services:
            add_spec_patch(region, services)
    for region, services in region_service_add_map.items():
        if services:
            add_spec_missing_services_patch(region, services)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
