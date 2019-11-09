"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import AVAILABILITY_ZONES, REGEX_CIDR


class Subnet(CloudFormationLintRule):
    """Check if EC2 Subnet Resource Properties"""
    id = 'E2510'
    shortdesc = 'Resource EC2 PropertiesEc2Subnet Properties'
    description = 'See if EC2 Subnet Properties are set correctly'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html'
    tags = ['properties', 'subnet']

    def check_az_value(self, value, path):
        """Check AZ Values"""
        matches = []

        if value not in AVAILABILITY_ZONES:
            message = 'Not a valid Availbility Zone {0} at {1}'
            matches.append(RuleMatch(path, message.format(value, ('/'.join(map(str, path))))))
        return matches

    def check_az_ref(self, value, path, parameters, resources):
        """Check ref for AZ"""
        matches = []
        allowed_types = [
            'AWS::EC2::AvailabilityZone::Name',
            'String',
            'AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>'
        ]
        if value in resources:
            message = 'AvailabilityZone can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(map(str, path))))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            param_type = parameter.get('Type', '')
            if param_type not in allowed_types:
                param_path = ['Parameters', value, 'Type']
                message = 'Availability Zone should be of type [{0}] for {1}'
                matches.append(
                    RuleMatch(
                        param_path,
                        message.format(
                            ', '.join(map(str, allowed_types)),
                            '/'.join(map(str, param_path)))))
        return matches

    def check_cidr_value(self, value, path):
        """Check CIDR Strings"""
        matches = []

        if not re.match(REGEX_CIDR, value):
            message = 'CidrBlock needs to be of x.x.x.x/y at {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(['Parameters', value])))))
        return matches

    def check_cidr_ref(self, value, path, parameters, resources):
        """Check CidrBlock for VPC"""
        matches = []

        allowed_types = [
            'String',
            'AWS::SSM::Parameter::Value<String>'
        ]

        if value in resources:
            resource_obj = resources.get(value, {})
            if resource_obj:
                resource_type = resource_obj.get('Type', '')
                if not resource_type.startswith('Custom::'):
                    message = 'CidrBlock needs to be a valid Cidr Range at {0}'
                    matches.append(RuleMatch(path, message.format(
                        ('/'.join(['Parameters', value])))))
        if value in parameters:
            parameter = parameters.get(value, {})
            parameter_type = parameter.get('Type', None)
            if parameter_type not in allowed_types:
                param_path = ['Parameters', value]
                message = 'CidrBlock Parameter should be of type [{0}] for {1}'
                matches.append(
                    RuleMatch(
                        param_path,
                        message.format(
                            ', '.join(map(str, allowed_types)),
                            '/'.join(map(str, param_path)))))
        return matches

    def check_vpc_value(self, value, path):
        """Check VPC Values"""
        matches = []

        if not value.startswith('vpc-'):
            message = 'VpcId needs to be of format vpc-xxxxxxxx at {1}'
            matches.append(RuleMatch(path, message.format(value, ('/'.join(map(str, path))))))
        return matches

    def check_vpc_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = []
        if value in resources:
            # Check if resource is a VPC
            message = 'VpcId can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(map(str, path))))))
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

        matches = []
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
