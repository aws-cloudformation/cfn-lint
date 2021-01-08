"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from datetime import date
import six
from cfnlint.helpers import convert_dict
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Policy(CloudFormationLintRule):
    """Check if IAM Policy JSON is correct"""
    id = 'E2507'
    shortdesc = 'Check if IAM Policies are properly configured'
    description = 'See if there elements inside an IAM policy are correct'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iam-policy.html'
    tags = ['properties', 'iam']

    def __init__(self):
        """Init"""
        super(Policy, self).__init__()
        self.resource_exceptions = {
            'AWS::ECR::Repository': 'RepositoryPolicyText',
        }
        self.resources_and_keys = {
            'AWS::ECR::Repository': 'RepositoryPolicyText',
            'AWS::Elasticsearch::Domain': 'AccessPolicies',
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
            'AWS::SSO::PermissionSet': 'InlinePolicy',
        }
        for resource_type in self.resources_and_keys:
            self.resource_property_types.append(resource_type)
        for resource_type in self.idp_and_keys:
            self.resource_property_types.append(resource_type)

    def check_policy_document(self, value, path, is_identity_policy, resource_exceptions, start_mark, end_mark):
        """Check policy document"""
        matches = []

        valid_keys = [
            'Version',
            'Id',
            'Statement',
        ]
        valid_versions = ['2012-10-17', '2008-10-17', date(2012, 10, 17), date(2008, 10, 17)]

        if isinstance(value, six.string_types):
            try:
                value = convert_dict(json.loads(value), start_mark, end_mark)
            except Exception as ex:  # pylint: disable=W0703,W0612
                message = 'IAM Policy Documents need to be JSON'
                matches.append(RuleMatch(path[:], message))
                return matches

        if not isinstance(value, dict):
            message = 'IAM Policy Documents needs to be JSON'
            matches.append(
                RuleMatch(path[:], message))
            return matches

        for p_vs, p_p in value.items_safe(path[:], (dict)):
            for parent_key, parent_value in p_vs.items():
                if parent_key not in valid_keys:
                    message = 'IAM Policy key %s doesn\'t exist.' % (parent_key)
                    matches.append(
                        RuleMatch(path[:] + p_p + [parent_key], message))
                if parent_key == 'Version':
                    if parent_value not in valid_versions:
                        message = 'IAM Policy Version needs to be one of (%s).' % (
                            ', '.join(map(str, ['2012-10-17', '2008-10-17'])))
                        matches.append(
                            RuleMatch(p_p + [parent_key], message))
                if parent_key == 'Statement':
                    if isinstance(parent_value, list):
                        for i_s_v, i_s_p in parent_value.items_safe(p_p + ['Statement'], (dict)):
                            matches.extend(
                                self._check_policy_statement(
                                    i_s_p, i_s_v, is_identity_policy, resource_exceptions
                                )
                            )
                    elif isinstance(parent_value, dict):
                        for i_s_v, i_s_p in parent_value.items_safe(p_p + ['Statement']):
                            matches.extend(
                                self._check_policy_statement(
                                    i_s_p, i_s_v, is_identity_policy, resource_exceptions
                                )
                            )
                    else:
                        message = 'IAM Policy statement should be of list.'
                        matches.append(
                            RuleMatch(p_p + [parent_key], message))
        return matches

    def _check_policy_statement(self, branch, statement, is_identity_policy, resource_exceptions):
        """Check statements"""
        matches = []
        statement_valid_keys = [
            'Action',
            'Condition',
            'Effect',
            'NotAction',
            'NotPrincipal',
            'NotResource',
            'Principal',
            'Resource',
            'Sid',
        ]

        for key, _ in statement.items():
            if key not in statement_valid_keys:
                message = 'IAM Policy statement key %s isn\'t valid' % (key)
                matches.append(
                    RuleMatch(branch[:] + [key], message))
        if 'Effect' not in statement:
            message = 'IAM Policy statement missing Effect'
            matches.append(
                RuleMatch(branch[:], message))
        else:
            for effect, effect_path in statement.get_safe('Effect'):
                if isinstance(effect, six.string_types):
                    if effect not in ['Allow', 'Deny']:
                        message = 'IAM Policy Effect should be Allow or Deny'
                        matches.append(
                            RuleMatch(branch[:] + effect_path, message))
        if 'Action' not in statement and 'NotAction' not in statement:
            message = 'IAM Policy statement missing Action or NotAction'
            matches.append(
                RuleMatch(branch[:], message))
        if is_identity_policy:
            if 'Principal' in statement or 'NotPrincipal' in statement:
                message = 'IAM Resource Policy statement shouldn\'t have Principal or NotPrincipal'
                matches.append(
                    RuleMatch(branch[:], message))
        else:
            if 'Principal' not in statement and 'NotPrincipal' not in statement:
                message = 'IAM Resource Policy statement should have Principal or NotPrincipal'
                matches.append(
                    RuleMatch(branch[:] + ['Principal'], message))
        if not resource_exceptions:
            if 'Resource' not in statement and 'NotResource' not in statement:
                message = 'IAM Policy statement missing Resource or NotResource'
                matches.append(
                    RuleMatch(branch[:], message))

        return(matches)

    def match_resource_properties(self, properties, resourcetype, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        is_identity_policy = True
        if resourcetype in self.resources_and_keys:
            is_identity_policy = False

        key = None
        if resourcetype in self.resources_and_keys:
            key = self.resources_and_keys.get(resourcetype)
        else:
            key = self.idp_and_keys.get(resourcetype)

        if not key:
            # Key isn't defined return nothing
            return matches

        resource_exceptions = False
        if key == self.resource_exceptions.get(resourcetype):
            resource_exceptions = True

        other_keys = []
        for key, value in self.resources_and_keys.items():
            if value != 'Policies':
                other_keys.append(key)
        for key, value in self.idp_and_keys.items():
            if value != 'Policies':
                other_keys.append(key)

        for key, value in properties.items():
            if key == 'Policies' and isinstance(value, list):
                for index, policy in enumerate(properties.get(key, [])):
                    matches.extend(
                        cfn.check_value(
                            obj=policy, key='PolicyDocument',
                            path=path[:] + ['Policies', index],
                            check_value=self.check_policy_document,
                            is_identity_policy=is_identity_policy,
                            resource_exceptions=resource_exceptions,
                            start_mark=key.start_mark, end_mark=key.end_mark,
                        ))
            elif key in ['KeyPolicy', 'PolicyDocument', 'RepositoryPolicyText', 'AccessPolicies', 'InlinePolicy']:
                matches.extend(
                    cfn.check_value(
                        obj=properties, key=key,
                        path=path[:],
                        check_value=self.check_policy_document,
                        is_identity_policy=is_identity_policy,
                        resource_exceptions=resource_exceptions,
                        start_mark=key.start_mark, end_mark=key.end_mark,
                    ))

        return matches
