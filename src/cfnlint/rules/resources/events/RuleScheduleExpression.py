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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class RuleScheduleExpression(CloudFormationLintRule):
    """Validate AWS Events Schedule expression format"""
    id = 'E3027'
    shortdesc = 'Validate AWS Event ScheduleExpression format'
    description = 'Validate the formation of the AWS::Event ScheduleExpression'
    source_url = 'https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html'
    tags = ['resources', 'events']

    def initialize(self, cfn):
        """Initialize the rule"""
        self.resource_property_types = ['AWS::Events::Rule']

    def check_rate(self, value, path):
        """Check Rate configuration"""
        matches = []
        # Extract the expression from rate(XXX)
        rate_expression = value[value.find('(')+1:value.find(')')]

        if not rate_expression:
            matches.append(RuleMatch(path, 'Rate value of ScheduleExpression cannot be empty'))
        else:
            # Rate format: rate(Value Unit)
            items = rate_expression.split(' ')

            if len(items) != 2:
                message = 'Rate expression must contain 2 elements (Value Unit), rate contains {} elements'
                matches.append(RuleMatch(path, message.format(len(items))))
            else:
                # Check the Value
                if not items[0].isdigit():
                    message = 'Rate Value ({}) should be of type Integer.'
                    matches.append(RuleMatch(path, message.format(items[0])))

        return matches

    def check_cron(self, value, path):
        """Check Cron configuration"""
        matches = []
        # Extract the expression from cron(XXX)
        cron_expression = value[value.find('(')+1:value.find(')')]

        if not cron_expression:
            matches.append(RuleMatch(path, 'Cron value of ScheduleExpression cannot be empty'))
        else:
            # Rate format: cron(Minutes Hours Day-of-month Month Day-of-week Year)
            items = cron_expression.split(' ')

            if len(items) != 6:
                message = 'Cron expression must contain 6 elements (Minutes Hours Day-of-month Month Day-of-week Year), cron contains {} elements'
                matches.append(RuleMatch(path, message.format(len(items))))

        return matches

    def check_value(self, value, path):
        """Count ScheduledExpression value"""
        matches = []

        # Value is either "cron()" or "rate()"
        if value.startswith('rate(') and value.endswith(')'):
            matches.extend(self.check_rate(value, path))
        elif value.startswith('cron(') and value.endswith(')'):
            matches.extend(self.check_cron(value, path))
        else:
            message = 'Invalid ScheduledExpression specified ({}). Value has to be either cron() or rate()'
            matches.append(RuleMatch(path, message.format(value)))

        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        matches.extend(
            cfn.check_value(
                obj=properties, key='ScheduleExpression',
                path=path[:],
                check_value=self.check_value
            ))

        return matches
