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
import datetime
import json

from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Limits(CloudFormationLintRule):
    """Check if IAM limits are not breached"""
    id = 'E2508'
    shortdesc = 'Check IAM resource limits'
    description = 'See if IAM resources do not breach limits'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['resources', 'iam']

    def _serialize_date(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        raise TypeError('Object of type {} is not JSON serializable'.format(obj.__class__.__name__))

    def check_managed_policy_arns(self, properties, path):
        """Check ManagedPolicyArns is within limits"""
        matches = []

        if 'ManagedPolicyArns' not in properties:
            return matches

        if len(properties['ManagedPolicyArns']) > 10:
            matches.append(
                RuleMatch(
                    path + ['ManagedPolicyArns'],
                    'IAM resources cannot have more than 10 ManagedPolicyArns',
                )
            )

        return matches

    def check_instance_profile_roles(self, properties, path):
        """Check InstanceProfile.Roles is within limits"""
        matches = []

        if 'Roles' not in properties:
            return matches

        if len(properties['Roles']) > 1:
            matches.append(
                RuleMatch(
                    path + ['Roles'],
                    'InstanceProfile can only have one role attached'
                )
            )

        return matches

    def check_user_groups(self, properties, path):
        """Check User.Groups is within limits"""
        matches = []

        if 'Groups' not in properties:
            return matches

        if len(properties['Groups']) > 10:
            matches.append(
                RuleMatch(
                    path + ['Groups'],
                    'User can be a member of maximum 10 groups',
                )
            )

        return matches

    def check_role_assume_role_policy_document(self, properties, path):
        """Check Role.AssumeRolePolicyDocument is within limits"""
        matches = []

        if 'AssumeRolePolicyDocument' not in properties:
            return matches

        if len(json.dumps(properties['AssumeRolePolicyDocument'], default=self._serialize_date)) > 2048:
            matches.append(
                RuleMatch(
                    path + ['AssumeRolePolicyDocument'],
                    'Role trust policy JSON text cannot be longer than 2048 characters',
                )
            )

        return matches

    def match(self, cfn):
        """Check that IAM resources are below limits"""
        matches = []
        types = {
            'AWS::IAM::User': [
                self.check_managed_policy_arns,
                self.check_user_groups,
            ],
            'AWS::IAM::Group': [
                self.check_managed_policy_arns,
            ],
            'AWS::IAM::Role': [
                self.check_managed_policy_arns,
                self.check_role_assume_role_policy_document,
            ],
            'AWS::IAM::InstanceProfile': [
                self.check_instance_profile_roles,
            ],
        }

        for resource_type, check_list in types.items():
            resources = cfn.get_resources(resource_type=resource_type)
            for resource_name, resource_object in resources.items():
                path = ['Resources', resource_name, 'Properties']
                properties = resource_object.get('Properties', {})
                for check in check_list:
                    matches.extend(check(properties, path))

        return matches
