"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class EventsLogGroupName(CloudFormationLintRule):
    """Check if the settings of multiple subscriptions are included for one LogGroup"""
    id = 'E2529'
    shortdesc = 'Check for SubscriptionFilters have beyond 2 attachments to a CloudWatch Log Group'
    description = 'The current limit for a CloudWatch Log Group is they can have 2 subscription filters. ' \
        'We will look for duplicate LogGroupNames inside Subscription Filters and make sure they are within 2. ' \
        'This doesn\'t account for any other subscription filters getting set.'
    source_url = 'https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#user-content-cloudwatchlogs'
    tags = ['resources', 'lambda']
    limit = 2

    def check_events_subscription_duplicated(self, cfn):
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        message = 'You can only have {} Subscription Filters per CloudWatch Log Group'.format(self.limit)

        log_group_paths = self.__get_log_group_name_list(cfn)
        for _, c in log_group_paths.items():
            if len(c) > self.limit:
                matches.append(
                    RuleMatch(
                        ['Resources', c[2]], message.format()
                    )
                )

        return matches

    def __get_log_group_name_list(self, cfn):
        log_group_paths = {}
        for value in cfn.get_resources('AWS::Logs::SubscriptionFilter').items():
            prop = value[1].get('Properties')
            log_group_name = json.dumps(prop.get('LogGroupName'))

            if log_group_name not in log_group_paths:
                log_group_paths[log_group_name] = []

            log_group_paths[log_group_name].append(value[0])
        return log_group_paths

    def match(self, cfn):
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        matches.extend(
            self.check_events_subscription_duplicated(cfn)
        )
        return matches
