"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.graph import Graph
from cfnlint.rules import RuleMatch

class CircularDependency(CloudFormationLintRule):
    """Check if Resources have a circular dependency"""
    id = 'E3004'
    shortdesc = 'Resource dependencies are not circular'
    description = 'Check that Resources are not circularly dependent by DependsOn, Ref, Sub, or GetAtt'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources', 'circularly', 'dependson', 'ref', 'sub', 'getatt']

    def match(self, cfn):
        matches = []

        graph = Graph(cfn)
        for cycle in graph.get_cycles(cfn):
            source, target = cycle[:2]
            message = 'Circular Dependencies for resource {0}. Circular dependency with [{1}]'.format(source,
                                                                                                      target)
            path = ['Resources', source]
            matches.append(RuleMatch(path, message))

        return matches
