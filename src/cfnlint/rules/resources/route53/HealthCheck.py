"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class HealthCheck(CloudFormationLintRule):
    """Check Route53 Recordset Configuration"""
    id = 'E3023'
    shortdesc = 'Validate that AlarmIdentifier is specified when using CloudWatch Metrics'
    description = 'When using a CloudWatch Metric for Route53 Health Checks you must also specify the AlarmIdentifier'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-healthcheck-healthcheckconfig.html#cfn-route53-healthcheck-healthcheckconfig-alarmidentifier'
    tags = ['resources', 'route53', 'alarm_identifier']

    def __init__(self):
        """Init"""
        super(HealthCheck, self).__init__()
        self.resource_sub_property_types = ['AWS::Route53::HealthCheck.HealthCheckConfig']

    def check(self, properties, path, cfn):
        """Check itself"""
        matches = []
        property_sets = cfn.get_object_without_conditions(properties)
        for property_set in property_sets:
            health_type = property_set.get('Object').get('Type')
            if health_type == 'CLOUDWATCH_METRIC':
                if 'AlarmIdentifier' not in property_set.get('Object'):
                    if property_set['Scenario'] is None:
                        message = '"AlarmIdentifier" must be specified when the check type is "CLOUDWATCH_METRIC" at {0}'
                        matches.append(RuleMatch(
                            path,
                            message.format('/'.join(map(str, path)))
                        ))
                    else:
                        scenario_text = ' and '.join(['when condition "%s" is %s' % (k, v) for (k, v) in property_set['Scenario'].items()])
                        message = '"AlarmIdentifier" must be specified when the check type is "CLOUDWATCH_METRIC" {0} at {1}'
                        matches.append(RuleMatch(
                            path,
                            message.format(scenario_text, '/'.join(map(str, path)))
                        ))

        return matches

    def match_resource_sub_properties(self, properties, _, path, cfn):
        """Match for sub properties"""
        matches = []

        matches.extend(self.check(properties, path, cfn))

        return matches
