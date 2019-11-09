"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Types(CloudFormationLintRule):
    """Check if Parameters are typed"""
    id = 'E2002'
    shortdesc = 'Parameters have appropriate type'
    description = 'Making sure the parameters have a correct type'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters']

    valid_types = [
        'AWS::EC2::AvailabilityZone::Name',
        'AWS::EC2::Image::Id',
        'AWS::EC2::Instance::Id',
        'AWS::EC2::KeyPair::KeyName',
        'AWS::EC2::SecurityGroup::GroupName',
        'AWS::EC2::SecurityGroup::Id',
        'AWS::EC2::Subnet::Id',
        'AWS::EC2::VPC::Id',
        'AWS::EC2::Volume::Id',
        'AWS::Route53::HostedZone::Id',
        'AWS::SSM::Parameter::Name',
        'CommaDelimitedList',
        'List<AWS::EC2::AvailabilityZone::Name>',
        'List<AWS::EC2::Image::Id>',
        'List<AWS::EC2::Instance::Id>',
        'List<AWS::EC2::SecurityGroup::GroupName>',
        'List<AWS::EC2::SecurityGroup::Id>',
        'List<AWS::EC2::Subnet::Id>',
        'List<AWS::EC2::VPC::Id>',
        'List<AWS::EC2::Volume::Id>',
        'List<AWS::Route53::HostedZone::Id>',
        'List<Number>',
        'List<String>',
        'Number',
        'String',
    ]

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        for paramname, paramvalue in cfn.get_parameters().items():
            # If the type isn't found we create a valid one
            # this test isn't about missing required properties for a
            # parameter.
            paramtype = paramvalue.get('Type', 'String')
            if paramtype not in self.valid_types:
                if not paramtype.startswith('AWS::SSM::Parameter::Value'):
                    message = 'Parameter {0} has invalid type {1}'
                    matches.append(RuleMatch(
                        ['Parameters', paramname, 'Type'],
                        message.format(paramname, paramtype)
                    ))

        return matches
