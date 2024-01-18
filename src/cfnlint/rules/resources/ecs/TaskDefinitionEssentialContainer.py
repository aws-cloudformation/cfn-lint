"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class TaskDefinitionEssentialContainer(BaseCfnSchema):
    """
    Check ECS TaskDefinition ContainerDefinitions Property
    Specifies at least one Essential Container
    """

    id = "E3042"
    shortdesc = "Validate at least one essential container is specified"
    description = (
        "Check that every TaskDefinition specifies at least one essential container"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-essential"
    tags = ["properties", "ecs", "task", "container", "fargate"]
    schema_path = "aws_ecs_taskdefinition/containerdefinitions_essential"
