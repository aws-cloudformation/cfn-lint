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


class SecurityGroupIngress(CloudFormationLintRule):
    """Check if EC2 Security Group Ingress Properties"""
    id = 'E2506'
    shortdesc = 'Resource EC2 Security Group Ingress Properties'
    description = 'See if EC2 Security Group Ingress Properties are set correctly. ' \
                  'Check that "SourceSecurityGroupId" or "SourceSecurityGroupName" are ' \
                  ' are exclusive and using the type of Ref or GetAtt '
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html'
    tags = ['resources', 'securitygroup']

    def check_sgid_value(self, value, path):
        """Check VPC Values"""
        matches = []
        if not value.startswith('sg-'):
            message = 'Security Group Id must have a valid Identifier {0}'
            matches.append(
                RuleMatch(path, message.format('/'.join(map(str, path)))))
        return matches

    def check_sgid_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = []

        allowed_types = [
            'AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>',
            'AWS::EC2::SecurityGroup::Id',
            'String'
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
        if value in resources:
            resource = resources.get(value, {})
            resource_type = resource.get('Type', '')
            if resource_type != 'AWS::EC2::SecurityGroup':
                message = 'Security Group Id resources should be of type AWS::EC2::SecurityGroup for {0}'
                matches.append(
                    RuleMatch(path, message.format('/'.join(map(str, path)))))
            else:
                resource_properties = resource.get('Properties', {})
                vpc_property = resource_properties.get('VpcId', None)
                if not vpc_property:
                    message = 'Security Group Id should reference a VPC based AWS::EC2::SecurityGroup for {0}'
                    matches.append(
                        RuleMatch(path, message.format('/'.join(map(str, path)))))

        return matches

    # pylint: disable=W0613
    def check_sgid_fail(self, value, path, **kwargs):
        """Automatic failure for certain functions"""

        matches = []
        message = 'Use Ref, FindInMap, or string values for {0}'
        matches.append(
            RuleMatch(path, message.format('/'.join(map(str, path)))))
        return matches

    def check_ingress_rule(self, vpc_id, properties, path, cfn):
        """Check ingress rule"""

        matches = []
        if vpc_id:

            # Check that SourceSecurityGroupName isn't specified
            if properties.get('SourceSecurityGroupName', None):
                path_error = path[:] + ['SourceSecurityGroupName']
                message = 'SourceSecurityGroupName shouldn\'t be specified for ' \
                          'Vpc Security Group at {0}'
                matches.append(
                    RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

            matches.extend(
                cfn.check_value(
                    obj=properties, key='SourceSecurityGroupId',
                    path=path[:],
                    check_value=self.check_sgid_value, check_ref=self.check_sgid_ref,
                    check_find_in_map=None, check_split=self.check_sgid_fail,
                    check_join=self.check_sgid_fail
                )
            )

        else:

            if properties.get('SourceSecurityGroupId', None):
                path_error = path[:] + ['SourceSecurityGroupId']
                message = 'SourceSecurityGroupId shouldn\'t be specified for ' \
                          'Non-Vpc Security Group at {0}'
                matches.append(
                    RuleMatch(path_error, message.format('/'.join(map(str, path_error)))))

        return matches

    def match(self, cfn):
        """Check EC2 Security Group Ingress Resource Parameters"""

        matches = []

        resources = cfn.get_resources(resource_type='AWS::EC2::SecurityGroup')
        for resource_name, resource_object in resources.items():
            properties = resource_object.get('Properties', {})
            if properties:
                vpc_id = properties.get('VpcId', None)
                ingress_rules = properties.get('SecurityGroupIngress')
                if isinstance(ingress_rules, list):
                    for index, ingress_rule in enumerate(ingress_rules):
                        path = [
                            'Resources', resource_name, 'Properties',
                            'SecurityGroupIngress', index
                        ]
                        matches.extend(
                            self.check_ingress_rule(
                                vpc_id=vpc_id,
                                properties=ingress_rule,
                                path=path,
                                cfn=cfn
                            )
                        )

        resources = None
        resources = cfn.get_resources(resource_type='AWS::EC2::SecurityGroupIngress')
        for resource_name, resource_object in resources.items():
            properties = resource_object.get('Properties', {})
            group_id = properties.get('GroupId', None)
            path = ['Resources', resource_name, 'Properties']
            if group_id:
                vpc_id = 'vpc-1234567'
            else:
                vpc_id = None

            if properties:
                path = ['Resources', resource_name, 'Properties']
                matches.extend(
                    self.check_ingress_rule(
                        vpc_id=vpc_id,
                        properties=properties,
                        path=path,
                        cfn=cfn
                    )
                )
        return matches
