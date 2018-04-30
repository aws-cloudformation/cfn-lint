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
import re
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Subnet(CloudFormationLintRule):
    """Check if EC2 Subnet Resource Properties"""
    id = 'E2510'
    shortdesc = 'Resource EC2 PropertiesEc2Subnet Properties'
    description = 'See if EC2 Subnet Properties are set correctly'
    tags = ['base', 'properties', 'subnet']

    # pylint: disable=C0301
    cidr_regex = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$'

    def check_az_value(self, value, path):
        """Check AZ Values"""
        matches = list()

        message = 'Don\'t hardcode {0} for AvailabilityZones at {1}'
        matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))
        return matches

    def check_az_ref(self, value, path, parameters, resources):
        """Check ref for AZ"""
        matches = list()
        if value in resources:
            message = 'AvailabilityZone can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')
            if param_type != 'AWS::EC2::AvailabilityZone::Name':
                param_path = ['Parameters', value, 'Type']
                message = 'Type for Parameter should be AWS::EC2::AvailabilityZone::Name for {0}'
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))
        return matches

    def check_cidr_value(self, value, path):
        """Check CIDR Strings"""
        matches = list()

        regex = re.compile(self.cidr_regex)
        if not regex.match(value):
            message = 'CidrBlock needs to be of x.x.x.x/y at {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(['Parameters', value])))))
        return matches

    def check_cidr_ref(self, value, path, parameters, resources):
        """Check CidrBlock for VPC"""
        matches = list()
        if value in resources:
            resource_obj = resources.get(value, {})
            if resource_obj:
                resource_type = resource_obj.get('Type', '')
                if not resource_type.startswith('Custom::'):
                    message = 'CidrBlock needs to be a valid Cidr Range at {0}'
                    matches.append(RuleMatch(path, message.format(('/'.join(['Parameters', value])))))
        if value in parameters:
            parameter = parameters.get(value, {})
            allowed_pattern = parameter.get('AllowedPattern', None)
            if not allowed_pattern:
                param_path = ['Parameters', value]
                message = 'AllowedPattern for Parameter should be specified at {1}. Example "{0}"'
                matches.append(RuleMatch(param_path, message.format(self.cidr_regex, ('/'.join(param_path)))))
        return matches

    def check_vpc_value(self, value, path):
        """Check VPC Values"""
        matches = list()

        if not value.startswith('vpc-'):
            message = 'VpcId needs to be of format vpc-xxxxxxxx at {1}'
            matches.append(RuleMatch(path, message.format(value, ('/'.join(path)))))
        return matches

    def check_vpc_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = list()
        if value in resources:
            # Check if resource is a VPC
            message = 'VpcId can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')
            if param_type != 'AWS::EC2::AvailabilityZone::Name':
                param_path = ['Parameters', value, 'Type']
                message = 'Type for Parameter should be AWS::EC2::AvailabilityZone::Name for {0}'
                matches.append(RuleMatch(param_path, message.format(('/'.join(param_path)))))
        return matches

    def match(self, cfn):
        """Check EC2 VPC Resource Parameters"""

        matches = list()
        matches.extend(
            cfn.check_resource_property(
                'AWS::EC2::Subnet', 'AvailabilityZone',
                check_value=self.check_az_value,
                check_ref=self.check_az_ref,
            )
        )
        matches.extend(
            cfn.check_resource_property(
                'AWS::EC2::Subnet', 'CidrBlock',
                check_value=self.check_cidr_value,
                check_ref=self.check_cidr_ref,
            )
        )

        return matches
