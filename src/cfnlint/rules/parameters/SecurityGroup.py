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


class SecurityGroup(CloudFormationLintRule):

    """Check if EC2 Security Group Ingress Properties"""
    id = 'W2507'
    shortdesc = 'Security Group Parameters are of correct type AWS::EC2::SecurityGroup::Id'
    description = 'Check if a parameter is being used in a resource for Security ' \
                  'Group.  If it is make sure it is of type AWS::EC2::SecurityGroup::Id'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters', 'securitygroup']

    def __init__(self):
        """Init"""
        resource_type_specs = [
            'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'AWS::AutoScaling::LaunchConfiguration',
            'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'AWS::EC2::Instance',
            'AWS::ElastiCache::ReplicationGroup',
            'AWS::DAX::Cluster',
            'AWS::ElastiCache::ReplicationGroup',
            'AWS::Glue::DevEndpoint',
            'AWS::EC2::SecurityGroupIngress',
        ]
        property_type_specs = [
            'AWS::EC2::LaunchTemplate.LaunchTemplateData',
            'AWS::Elasticsearch::Domain.VPCOptions',
            'AWS::Lambda::Function.VpcConfig',
            'AWS::Batch::ComputeEnvironment.ComputeResources',
            'AWS::CodeBuild::Project.VpcConfig',
            'AWS::EC2::SecurityGroup.Ingress',
        ]

        for resoruce_type_spec in resource_type_specs:
            self.resource_property_types.append(resoruce_type_spec)
        for property_type_spec in property_type_specs:
            self.resource_sub_property_types.append(property_type_spec)

    # pylint: disable=W0613
    def check_sgid_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = []
        if 'SourceSecurityGroupId' in path:
            allowed_types = [
                'AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>',
                'AWS::EC2::SecurityGroup::Id'
            ]
        elif isinstance(path[-2], int):
            allowed_types = [
                'AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>',
                'AWS::EC2::SecurityGroup::Id'
            ]
        else:
            allowed_types = [
                'AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::Id>>',
                'List<AWS::EC2::SecurityGroup::Id>'
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

    def check(self, properties, resource_type, path, cfn):
        """Check itself"""
        matches = []

        matches.extend(
            cfn.check_value(
                properties, 'SecurityGroupIds', path,
                check_value=None, check_ref=self.check_sgid_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'SecurityGroups', path,
                check_value=None, check_ref=self.check_sgid_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'SourceSecurityGroupId', path,
                check_value=None, check_ref=self.check_sgid_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        matches.extend(self.check(properties, property_type, path, cfn))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        matches.extend(self.check(properties, resource_type, path, cfn))

        return matches
