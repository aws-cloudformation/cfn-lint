"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from datetime import date
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class PolicyVersion(CloudFormationLintRule):
    """Check if IAM Policy Version is correct"""
    id = 'W2511'
    shortdesc = 'Check IAM Resource Policies syntax'
    description = 'See if the elements inside an IAM Resource policy are configured correctly.'
    source_url = 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html'
    tags = ['properties', 'iam']

    def __init__(self):
        """Init"""
        super(PolicyVersion, self).__init__()
        self.resources_and_keys = {
            'AWS::ECR::Repository': 'RepositoryPolicyText',
            'AWS::Elasticsearch::Domain': 'AccessPolicies',
            'AWS::OpenSearchService::Domain': 'AccessPolicies',
            'AWS::KMS::Key': 'KeyPolicy',
            'AWS::S3::BucketPolicy': 'PolicyDocument',
            'AWS::SNS::TopicPolicy': 'PolicyDocument',
            'AWS::SQS::QueuePolicy': 'PolicyDocument',
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
