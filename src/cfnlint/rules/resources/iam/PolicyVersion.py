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
from datetime import date
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class PolicyVersion(CloudFormationLintRule):
    """Check if IAM Policy Version is correct"""
    id = 'W2511'
    shortdesc = 'Check IAM Resource Policies syntax'
    description = 'See if the elements inside an IAM Resource policy ' + \
                  'are configured correctly.'
    source_url = 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html'
    tags = ['properties', 'iam']

    def __init__(self):
        """Init"""
        self.resources_and_keys = {
            'AWS::SNS::TopicPolicy': 'PolicyDocument',
            'AWS::S3::BucketPolicy': 'PolicyDocument',
            'AWS::KMS::Key': 'KeyPolicy',
            'AWS::SQS::QueuePolicy': 'PolicyDocument',
            'AWS::ECR::Repository': 'RepositoryPolicyText',
            'AWS::Elasticsearch::Domain': 'AccessPolicies',
        }
        self.idp_and_keys = {
            'AWS::IAM::Group': 'Policies',
            'AWS::IAM::ManagedPolicy': 'PolicyDocument',
            'AWS::IAM::Policy': 'PolicyDocument',
            'AWS::IAM::Role': 'Policies',
            'AWS::IAM::User': 'Policies',
        }
        for resource_type in self.resources_and_keys:
            self.resource_property_types.append(resource_type)
        for resource_type in self.idp_and_keys:
            self.resource_property_types.append(resource_type)

    def check_policy_document(self, value, path):
        """Check policy document"""
        matches = []

        if not isinstance(value, dict):
            return matches

        for e_v, e_p in value.items_safe(path[:]):
            for p_vs, p_p in e_v.items_safe(e_p[:]):
                version = p_vs.get('Version')
                if version:
                    if version in ['2008-10-17', date(2008, 10, 17)]:
                        message = 'IAM Policy Version should be updated to \'2012-10-17\'.'
                        matches.append(
                            RuleMatch(p_p + ['Version'], message))
        return matches

    def match_resource_properties(self, properties, resourcetype, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        key = None
        if resourcetype in self.resources_and_keys:
            key = self.resources_and_keys.get(resourcetype)
        else:
            key = self.idp_and_keys.get(resourcetype)

        if key == 'Policies':
            for index, policy in enumerate(properties.get(key, [])):
                matches.extend(
                    cfn.check_value(
                        obj=policy, key='PolicyDocument',
                        path=path[:] + ['Policies', index],
                        check_value=self.check_policy_document,
                    ))
        else:
            matches.extend(
                cfn.check_value(
                    obj=properties, key=key,
                    path=path[:],
                    check_value=self.check_policy_document
                ))

        return matches
