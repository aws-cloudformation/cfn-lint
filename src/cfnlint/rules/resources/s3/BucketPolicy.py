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
import re
import json
import six
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import convert_dict, load_resource


class BucketPolicy(CloudFormationLintRule):
    """Check if a S3 Bucket has a bucket policy"""
    id = 'E3027'
    shortdesc = 'Validate a S3 bucket\'s policy'
    description = 'Check that a S3 Bucket Policy is syntactically correct'
    source_url = 'https://docs.aws.amazon.com/AmazonS3/latest/dev/using-iam-policies.html'
    tags = ['resources', 's3']

    def __init__(self):
        """Init"""
        super(BucketPolicy, self).__init__()
        self.resource_property_types = ['AWS::S3::BucketPolicy']
        self.s3_actions = load_resource(
            AdditionalSpecs, 'Policies.json').get('serviceMap').get('Amazon S3').get('Actions')
        self.s3_object_actions = [
            'AbortMultipartUpload',
            'ListMultipartUploadParts',
            'BypassGovernanceRetention'
        ]

    # pylint: disable=W0613
    def check_value(self, value, path, start_mark, end_mark, bucket_resources, custom_resources):
        """Count them up """

        if isinstance(value, six.string_types):
            try:
                value = convert_dict(json.loads(value), start_mark, end_mark)
            except Exception as ex:  # pylint: disable=W0703,W0612
                return []

        if isinstance(value, dict):
            return self._check_policy(value, path[:], bucket_resources, custom_resources)

        return []

    def _check_policy(self, policy, path, bucket_resources, custom_resources):
        """ Check the entire policy """
        matches = []

        key = 'Statement'
        for statements, statements_path in policy.get_safe(key, default=[], path=path[:]):
            if isinstance(statements, list):
                for statement, statement_path in statements.items_safe(path=statements_path[:]):
                    matches.extend(
                        self._check_statement(
                            statement, statement_path[:],
                            bucket_resources, custom_resources))

        return matches

    def _check_statement(self, value, path, bucket_resources, custom_resources):
        """ Check each statement"""
        matches = []

        actions = value.get('Action')
        if not isinstance(actions, (list, six.string_types)):
            return matches
        resources = value.get('Resource')
        if not isinstance(resources, (list, six.string_types, dict)):
            return matches

        if isinstance(actions, six.string_types):
            actions = [actions]
        if isinstance(resources, (six.string_types, dict)):
            resources = [resources]

        found_object_actions, found_bucket_actions, actions_results_conclusive = self._get_statement_actions(
            actions)
        found_object_resources, found_bucket_resources, bucket_results_conclusive = self._get_statement_resources(
            resources, bucket_resources, custom_resources)
        if not actions_results_conclusive or not bucket_results_conclusive:
            return matches

        if (not found_object_resources) and found_object_actions:
            message = 'S3 Bucket Policy has object actions and no specified object resource'
            matches.append(RuleMatch(path[:] + ['Resource'], message))
        elif not found_bucket_resources and found_bucket_actions:
            message = 'S3 Bucket Policy has bucket actions and no specified bucket resource'
            matches.append(RuleMatch(path[:] + ['Resource'], message))

        return matches

    def _get_statement_actions(self, actions):
        """ Breaks down the actions in a statement to each category """
        # print(self.s3_actions)
        object_actions = list(filter(re.compile('.*Object.*').match, self.s3_actions))
        object_actions.extend(self.s3_object_actions)

        bucket_actions = [
            's3:' + action for action in list(set(self.s3_actions) - set(object_actions))]
        object_actions = ['s3:' + action for action in object_actions]

        found_object_actions = []
        found_bucket_actions = []
        for action in actions:
            if action in object_actions:
                found_object_actions.append(action)
            elif action in bucket_actions:
                found_bucket_actions.append(action)
            else:
                return None, None, False

        return found_object_actions, found_bucket_actions, True

    def _get_statement_resources(self, resources, bucket_resources, custom_resources):
        """ Get Statement Resources """
        found_bucket_resources = False
        found_object_resources = False
        for resource in resources:
            if isinstance(resource, dict):
                if len(resource) == 1:
                    for func, func_value in resource.items():
                        if func == 'Fn::Sub':
                            if isinstance(func_value, six.string_types):
                                if re.match('.+/.+', func_value):  # pylint: disable=R1703
                                    found_object_resources = True
                                else:
                                    found_bucket_resources = True
                            else:
                                # Too many paths to compute at this point
                                return None, None, False
                        elif func == 'Fn::GetAtt':
                            if isinstance(func_value, six.string_types):
                                func_value = func_value.split('.', 1)
                            if func_value[0] in custom_resources:
                                return None, None, False
                            if func_value[0] in bucket_resources:
                                found_bucket_resources = True
                        else:
                            # Too many options or just invalid items
                            return None, None, False
            elif isinstance(resource, six.string_types):
                if re.match('.+/.+', resource):  # pylint: disable=R1703
                    found_object_resources = True
                else:
                    found_bucket_resources = True

        return found_object_resources, found_bucket_resources, True

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        key = 'PolicyDocument'

        bucket_resources = cfn.get_resources(resource_type=['AWS::S3::Bucket'])
        custom_resources = cfn.get_resources(
            resource_type=['AWS::CloudFormation::CustomResource', 'AWS::CloudFormation::Stack'],
            resource_prefix=['Custom::']
        )
        matches.extend(
            cfn.check_value(
                obj=properties, key=key,
                path=path[:],
                check_value=self.check_value,
                start_mark=properties.get(key).start_mark, end_mark=properties.get(key).end_mark,
                bucket_resources=bucket_resources.keys(),
                custom_resources=custom_resources.keys(),
            ))

        return matches
