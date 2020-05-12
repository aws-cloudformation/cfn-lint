"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


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
                    extra_args = {'actual_type': type(
                        items[0]).__name__, 'expected_type': int.__name__}
                    matches.append(RuleMatch(path, message.format(items[0]), **extra_args))

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

            _, _, day_of_month, _, day_of_week, _ = cron_expression.split(' ')
            if day_of_month != '?' and day_of_week != '?':
                matches.append(RuleMatch(
                    path, 'Don\'t specify the Day-of-month and Day-of-week fields in the same cron expression'))

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
