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


class EventsLogGroupName(CloudFormationLintRule):
    """Check if the settings of multiple subscriptions are included for one LogGroup"""
    id = 'E2529'
    shortdesc = 'Check for duplicate Lambda events'
    description = 'Check if there are any duplicate log groups in the Lambda event trigger element.'
    source_url = 'https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#user-content-cloudwatchlogs'
    tags = ['resources', 'lambda']

    def check_events_subscription_deprecated(self, cfn):
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

    def __is_duplicated(self, list):
        unique_list = self.__remove(list)
        return len(unique_list) != len(list)

    def __remove(self, duplicate):
        final_list = []
        for ele in duplicate:
            if ele not in final_list:
                final_list.append(ele)
        return final_list

    def __get_log_group_name_list(self, cfn):
        log_group_name_list = []
        for key, value in cfn.get_resources('AWS::Logs::SubscriptionFilter').items():
            log_group_name_list.append(value.get('Properties').get('LogGroupName'))
        return log_group_name_list

    def match(self, cfn):
        matches = []
        matches.extend(
            self.check_events_subscription_deprecated(cfn)
        )
        return matches
