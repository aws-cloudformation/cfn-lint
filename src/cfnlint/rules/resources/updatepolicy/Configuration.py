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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Configuration(CloudFormationLintRule):
    """Check Update Policy Configuration"""
    id = 'E3016'
    shortdesc = 'Check the configuration of a resources UpdatePolicy'
    description = 'Make sure a resources UpdatePolicy is properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html'
    tags = ['resources', 'updatepolicy']
    valid_attributes = {
        'sub': {
            'AutoScalingReplacingUpdate': {
                'WillReplace': {
                    'PrimitiveType': 'Boolean'
                }
            },
            'AutoScalingRollingUpdate': {
                'MaxBatchSize': {
                    'PrimitiveType': 'Integer'
                },
                'MinInstancesInService': {
                    'PrimitiveType': 'Integer'
                },
                'MinSuccessfulInstancesPercent': {
                    'PrimitiveType': 'Integer'
                },
                'PauseTime': {
                    'PrimitiveType': 'String'
                },
                'SuspendProcesses': {
                    'PrimitiveType': 'List',
                    'ValidValues': [
                        'Launch', 'Terminate', 'HealthCheck',
                        'ReplaceUnhealthy', 'AZRebalance', 'AlarmNotification',
                        'ScheduledActions', 'AddToLoadBalancer'
                    ]
                },
                'WaitOnResourceSignals': {
                    'PrimitiveType': 'Boolean'
                }
            },
            'AutoScalingScheduledAction': {
                'IgnoreUnmodifiedGroupSizeProperties': {
                    'PrimitiveType': 'Boolean'
                }
            },
            'CodeDeployLambdaAliasUpdate': {
                'AfterAllowTrafficHook': {
                    'PrimitiveType': 'String'
                },
                'ApplicationName': {
                    'PrimitiveType': 'String'
                },
                'BeforeAllowTrafficHook': {
                    'PrimitiveType': 'String'
                },
                'DeploymentGroupName': {
                    'PrimitiveType': 'String'
                },
            }
        },
        'main': {
            'AutoScalingReplacingUpdate': {
                'Type': 'AutoScalingReplacingUpdate',
                'ResourceTypes': [
                    'AWS::AutoScaling::AutoScalingGroup'
                ]
            },
            'AutoScalingRollingUpdate': {
                'Type': 'AutoScalingRollingUpdate',
                'ResourceTypes': [
                    'AWS::AutoScaling::AutoScalingGroup'
                ]
            },
            'AutoScalingScheduledAction': {
                'Type': 'AutoScalingScheduledAction',
                'ResourceTypes': [
                    'AWS::AutoScaling::AutoScalingGroup'
                ]
            },
            'CodeDeployLambdaAliasUpdate': {
                'Type': 'CodeDeployLambdaAliasUpdate',
                'ResourceTypes': [
                    'AWS::Lambda::Alias'
                ]
            },
            'UseOnlineResharding': {
                'PrimitiveType': 'Boolean',
                'ResourceTypes': [
                    'AWS::ElastiCache::ReplicationGroup'
                ]
            }
        },
        'primitive_types': {
            'String': six.string_types,
            'Integer': int,
            'Boolean': bool,
            'List': list
        }
    }

    def check_primitive_type(self, value, prim_type, path, **kwargs):
        """
            Check primitive types
        """
        matches = []

        if isinstance(value, dict):
            # this could be a ref, getatt, findinmap
            return matches

        default_message = 'Value for {0} must be of type {1}'
        if not isinstance(value, self.valid_attributes.get('primitive_types').get(prim_type)):
            matches.append(
                RuleMatch(path, default_message.format(path[-1], prim_type)))

        if prim_type == 'List' and isinstance(value, list):
            valid_values = kwargs.get('valid_values')
            if valid_values:
                for l_value in value:
                    if l_value not in valid_values:
                        message = 'Allowed values for {0} are ({1})'
                        matches.append(
                            RuleMatch(path, message.format(path[-1], ', '.join(map(str, valid_values)))))

        return matches

    def check_attributes(self, properties, spec_type, path):
        """
            Check the properties against the spec
        """
        matches = []
        spec = self.valid_attributes.get('sub').get(spec_type)
        if isinstance(properties, dict):
            for p_name, p_value in properties.items():
                if p_name in spec:
                    up_type_spec = spec.get(p_name)
                    if 'Type' in up_type_spec:
                        matches.extend(
                            self.check_attributes(
                                p_value, up_type_spec.get('Type'), path[:] + [p_name]))
                    else:
                        matches.extend(
                            self.check_primitive_type(
                                p_value, up_type_spec.get('PrimitiveType'),
                                path[:] + [p_name],
                                valid_values=up_type_spec.get('ValidValues', [])))
                else:
                    message = 'UpdatePolicy doesn\'t support type {0}'
                    matches.append(
                        RuleMatch(path[:] + [p_name], message.format(p_name)))
        else:
            message = '{0} should be an object'
            matches.append(
                RuleMatch(path, message.format(path[-1])))

        return matches

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        for r_name, r_values in cfn.get_resources().items():
            update_policy = r_values.get('UpdatePolicy', {})
            resource_type = r_values.get('Type')
            if isinstance(update_policy, dict):
                for up_type, up_value in update_policy.items():
                    path = ['Resources', r_name, 'UpdatePolicy', up_type]
                    up_type_spec = self.valid_attributes.get('main').get(up_type)
                    if up_type_spec:
                        if resource_type not in up_type_spec.get('ResourceTypes'):
                            message = 'UpdatePolicy only supports this type for resources of type ({0})'
                            matches.append(
                                RuleMatch(path, message.format(', '.join(map(str, up_type_spec.get('ResourceTypes'))))))
                        if 'Type' in up_type_spec:
                            matches.extend(
                                self.check_attributes(
                                    up_value, up_type_spec.get('Type'), path[:]))

                        else:
                            matches.extend(
                                self.check_primitive_type(
                                    up_value, up_type_spec.get('PrimitiveType'),
                                    path[:],
                                    valid_values=up_type_spec.get('ValidValues', [])))
                    else:
                        message = 'UpdatePolicy doesn\'t support type {0}'
                        matches.append(
                            RuleMatch(path, message.format(up_type)))
            else:
                message = 'UpdatePolicy should be an object'
                matches.append(
                    RuleMatch(['Resources', r_name, 'UpdatePolicy'], message.format(path[-1])))

        return matches
