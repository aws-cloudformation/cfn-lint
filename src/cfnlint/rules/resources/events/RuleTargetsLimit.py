"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


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
        self.resource_property_types.append('AWS::Events::Rule')
        self.limits = {}

    # pylint: disable=W0613
    def check_value(self, value, path):
        """Count them up """
        if path[4] == 'Fn::If':
            resource_name = '%s.%s' % (path[1], path[5])
        else:
            resource_name = path[1]
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
