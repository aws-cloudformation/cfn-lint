"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RuleTargetsLimit(CloudFormationLintRule):
    """Check State Machine Definition"""
    id = 'E3021'
    shortdesc = 'Check Events Rule Targets are less than or equal to 5'
    description = 'CloudWatch Events Rule can only support up to 5 targets'
    source_url = 'https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/cloudwatch_limits_cwe.html'
    tags = ['resources', 'events']
    max_count = 5

    def __init__(self):
        """Init"""
        super(RuleTargetsLimit, self).__init__()
        self.resource_property_types = ['AWS::Events::Rule']
        self.limits = {}

    def initialize(self, cfn):
        self.limits = {}

    # pylint: disable=W0613
    def check_value(self, value, path):
        """Count them up """

        resource_name = path[1]
        if len(path) > 4:
            if path[4] == 'Fn::If':
                resource_name = '%s.%s' % (path[1], path[5])

        if resource_name not in self.limits:
            self.limits[resource_name] = {
                'count': 0,
                'path': path[:-1]
            }

        self.limits[resource_name]['count'] += 1
        return []

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []
        matches.extend(
            cfn.check_value(
                obj=properties, key='Targets',
                path=path[:],
                check_value=self.check_value
            ))

        for _, limit in self.limits.items():
            if limit['count'] > self.max_count:
                message = 'An Events Rule can have up to {0} Targets'
                matches.append(RuleMatch(limit['path'], message.format(self.max_count)))

        return matches
