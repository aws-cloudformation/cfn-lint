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
import six

from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch

import cfnlint.helpers


class Permissions(CloudFormationLintRule):
    """Check IAM Permission configuration"""
    id = 'W3037'
    shortdesc = 'Check IAM Permission configuration'
    description = 'Check for valid IAM Permissions'
    source_url = 'https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_action.html'
    tags = ['properties', 'iam', 'permissions']
    experimental = True

    IAM_PERMISSION_RESOURCE_TYPES = [
        'AWS::IAM::ManagedPolicy',
        'AWS::IAM::Policy',
        'AWS::SNS::TopicPolicy',
        'AWS::SQS::QueuePolicy'
    ]

    def load_service_map(self):
        """
        Convert policies.json into a simpler version for more efficient key lookup.
        """
        service_map = cfnlint.helpers.load_resources('/data/AdditionalSpecs/Policies.json')['serviceMap']

        policy_service_map = {}

        for _, properties in service_map.items():
            # The services and actions are case insensitive
            service = properties['StringPrefix'].lower()
            actions = [x.lower() for x in properties['Actions']]

            # Some services have the same name for different generations; like elasticloadbalancing.
            if service in policy_service_map:
                policy_service_map[service] += actions
            else:
                policy_service_map[service] = actions

        return policy_service_map

    def check_permissions(self, action, path, service_map):
        """
        Check if permission is valid
        """
        matches = []

        if action == '*':
            return matches

        service, permission = action.split(':')
        # Get lowercase so we can check case insenstive. Keep the original values for the message
        service_value = service.lower()
        permission_value = permission.lower()

        if service_value in service_map:
            if permission_value.endswith('*'):
                wilcarded_permission = permission_value.split('*')[0]
                if not any(wilcarded_permission in action for action in service_map[service_value]):
                    message = 'Invalid permission "{}" for "{}" found in permissions'
                    matches.append(
                        RuleMatch(
                            path,
                            message.format(permission, service, '/'.join(path))))

            elif permission_value.startswith('*'):
                wilcarded_permission = permission_value.split('*')[1]
                if not any(wilcarded_permission in action for action in service_map[service_value]):
                    message = 'Invalid permission "{}" for "{}" found in permissions'
                    matches.append(
                        RuleMatch(
                            path,
                            message.format(permission, service, '/'.join(path))))
            elif permission_value not in service_map[service_value]:
                message = 'Invalid permission "{}" for "{}" found in permissions'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(permission, service, '/'.join(path))))
        else:
            message = 'Invalid service "{}" found in permissions'
            matches.append(
                RuleMatch(
                    path,
                    message.format(service, '/'.join(path))))

        return matches

    def get_actions(self, effective_permissions):
        """return all actions from a statement"""

        actions = []

        if 'Action' in effective_permissions:
            if isinstance(effective_permissions.get('Action'), six.string_types):
                actions.append(effective_permissions.get('Action'))
            elif isinstance(effective_permissions.get('Action'), list):
                actions.extend(effective_permissions.get('Action'))

        if 'NotAction' in effective_permissions:
            if isinstance(effective_permissions.get('NotAction'), six.string_types):
                actions.append(effective_permissions.get('NotAction'))
            elif isinstance(effective_permissions.get('Action'), list):
                actions.extend(effective_permissions.get('NotAction'))

        return actions

    def match(self, cfn):
        """Check IAM Permissions"""
        matches = []

        statements = []
        service_map = self.load_service_map()
        for resource_type in self.IAM_PERMISSION_RESOURCE_TYPES:
            statements.extend(cfn.get_resource_properties([resource_type, 'PolicyDocument', 'Statement']))

        for statement in statements:
            path = statement['Path']
            effective_permissions = statement['Value']

            actions = []

            if isinstance(effective_permissions, dict):
                actions.extend(self.get_actions(effective_permissions))

            elif isinstance(effective_permissions, list):
                for effective_permission in effective_permissions:
                    actions.extend(self.get_actions(effective_permission))

            for action in actions:
                matches.extend(self.check_permissions(action, path, service_map))

        return matches
