"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class TaskDefinitionEssentialContainer(CloudFormationLintRule):
    """Check ECS TaskDefinition ContainerDefinitions Property Specifies at least one Essential Container"""
    id = 'E3042'
    shortdesc = 'Check at least one essential container is specified'
    description = 'Check that every TaskDefinition specifies at least one essential container'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ecs-taskdefinition-containerdefinitions.html#cfn-ecs-taskdefinition-containerdefinition-essential'
    tags = ['properties', 'ecs', 'task', 'container', 'fargate']

    def match(self, cfn):
        """Check at least one essential container is specified"""

        matches = []

        results = cfn.get_resource_properties(['AWS::ECS::TaskDefinition', 'ContainerDefinitions'])

        for result in results:
            path = result['Path']

            has_essential_container = False

            for container in result['Value']:
                if 'Essential' in container:
                    if container['Essential']:
                        has_essential_container = True
                    else:
                        pass
                else:
                    # If 'Essential' is not specified, it defaults to an essential container
                    has_essential_container = True

            if not has_essential_container:
                message = 'No essential containers defined for {0}'
                rule_match = RuleMatch(path, message.format('/'.join(map(str, path))))
                matches.append(rule_match)

        return matches
