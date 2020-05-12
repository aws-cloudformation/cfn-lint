"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class EventsLogGroupName(CloudFormationLintRule):
    """Check if the settings of multiple subscriptions are included for one LogGroup"""
    id = 'E2529'
    shortdesc = 'Check for duplicate Lambda events'
    description = 'Check if there are any duplicate log groups in the Lambda event trigger element.'
    source_url = 'https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#user-content-cloudwatchlogs'
    tags = ['resources', 'lambda']

    def check_events_subscription_duplicated(self, cfn):
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        message = 'You must specify the AWS::Serverless::Function event correctly. ' \
                  'LogGroups are duplicated. '

        log_group_name_list = self.__get_log_group_name_list(cfn)

        if self.__is_duplicated(log_group_name_list):
            matches.append(
                RuleMatch(
                    'path', message.format()
                )
            )

        return matches

    def __is_duplicated(self, duplicate_list):
        unique_list = self.__remove(duplicate_list)
        return len(unique_list) != len(duplicate_list)

    def __remove(self, duplicate):
        final_list = []
        for ele in duplicate:
            if ele not in final_list:
                final_list.append(ele)
        return final_list

    def __get_log_group_name_list(self, cfn):
        log_group_name_list = []
        for value in cfn.get_resources('AWS::Logs::SubscriptionFilter').items():
            prop = value[1].get('Properties')
            log_group_name_list.append(prop.get('LogGroupName'))
        return log_group_name_list

    def match(self, cfn):
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        matches.extend(
            self.check_events_subscription_duplicated(cfn)
        )
        return matches
