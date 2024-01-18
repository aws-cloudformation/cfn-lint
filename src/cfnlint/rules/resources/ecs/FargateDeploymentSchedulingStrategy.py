"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class FargateDeploymentSchedulingStrategy(BaseCfnSchema):
    id = "E3044"
    shortdesc = (
        "ECS service using FARGATE or EXTERNAL can only "
        "use SchedulingStrategy of REPLICA"
    )
    description = (
        "When using a TargetType of Fargate or External the SchedulingStrategy "
        "has to be Replica"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-schedulingstrategy"
    tags = ["properties", "ecs", "service", "container", "fargate"]
    schema_path = "aws_ecs_service/fargate"
