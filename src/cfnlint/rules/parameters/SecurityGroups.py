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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class SecurityGroups(CloudFormationLintRule):
    """Check if EC2 Security Group Ingress Properties"""
    id = 'W2507'
    shortdesc = 'Security Group Parameters are of correct type AWS::EC2::SecurityGroup::Id'
    description = 'Check if a parameter is being used in a resource for Security ' \
                  'Group.  If it is make sure it is of type AWS::EC2::SecurityGroup::Id'
    tags = ['base', 'parameters', 'securitygroup']

    # pylint: disable=W0613
    def check_sgid_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = list()
        allowed_types = [
            'AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>',
            'AWS::EC2::SecurityGroup::Id'
        ]
        if value in parameters:
            parameter_properties = parameters.get(value)
            parameter_type = parameter_properties.get('Type')
            if parameter_type not in allowed_types:
                path_error = ['Parameters', value, 'Type']
                message = 'Security Group Id Parameter should be of type [{0}] for {1}'
                matches.append(
                    RuleMatch(
                        path_error,
                        message.format(
                            ', '.join(map(str, allowed_types)),
                            '/'.join(map(str, path_error)))))

        return matches

    def match(self, cfn):
        """Check EC2 Security Group Parameters"""

        matches = list()
        resources = [
            {
                'type': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
                'property': 'SecurityGroups'
            },
            {
                'type': 'AWS::AutoScaling::LaunchConfiguration',
                'property': 'SecurityGroups'
            },
            {
                'type': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
                'property': 'SecurityGroups'
            },
            {
                'type': 'AWS::EC2::Instance',
                'property': 'SecurityGroupIds'
            },
            {
                'type': 'AWS::ElastiCache::ReplicationGroup',
                'property': 'SecurityGroupIds'
            },
            {
                'type': 'AWS::DAX::Cluster',
                'property': 'SecurityGroupIds'
            },
            {
                'type': 'AWS::ElastiCache::ReplicationGroup',
                'property': 'SecurityGroupIds'
            },
            {
                'type': 'AWS::Glue::DevEndpoint',
                'property': 'SecurityGroupIds'
            }
        ]
        for resource in resources:
            matches.extend(
                cfn.check_resource_property(
                    resource['type'], resource['property'],
                    check_value=None, check_ref=self.check_sgid_ref,
                    check_mapping=None, check_split=None,
                    check_join=None))
        return matches
