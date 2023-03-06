"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class FargateDeploymentSchedulingStrategy(CloudFormationLintRule):
    id = "E3044"
    shortdesc = "Check Fargate service scheduling strategy"
    description = "Check that Fargate service scheduling strategy is REPLICA"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-schedulingstrategy"
    tags = ["properties", "ecs", "service", "container", "fargate"]

    def match(self, cfn):
        matches = []
        ecs_services = cfn.get_resource_properties(["AWS::ECS::Service"])

        for ecs_service in ecs_services:
            path = ecs_service["Path"]
            properties = ecs_service["Value"]
            if isinstance(properties, dict):
                scenarios = cfn.get_object_without_conditions(
                    properties, ["LaunchType", "SchedulingStrategy"]
                )
                for scenario in scenarios:
                    props = scenario.get("Object")
                    launch_type = props.get("LaunchType", None)
                    if isinstance(launch_type, str) and launch_type == "FARGATE":
                        scheduling_strategy = props.get("SchedulingStrategy", None)
                        if (
                            isinstance(scheduling_strategy, str)
                            and scheduling_strategy != "REPLICA"
                        ):
                            error_message = f"Fargate service only support REPLICA as scheduling strategy at {'/'.join(map(str, path))}"
                            matches.append(RuleMatch(path, error_message))
        return matches
