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


class Types(CloudFormationLintRule):
    """Check if Parameters are typed"""
    id = 'E2002'
    shortdesc = 'Parameters have appropriate type'
    description = 'Making sure the parameters have a correct type'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes'
    tags = ['parameters']

    valid_types = [
        'String',
        'Number',
        'List<Number>',
        'CommaDelimitedList',
        'AWS::EC2::AvailabilityZone::Name',
        'AWS::EC2::Image::Id',
        'AWS::EC2::Instance::Id',
        'AWS::EC2::KeyPair::KeyName',
        'AWS::EC2::SecurityGroup::GroupName',
        'AWS::EC2::SecurityGroup::Id',
        'AWS::EC2::Subnet::Id',
        'AWS::EC2::Volume::Id',
        'AWS::EC2::VPC::Id',
        'AWS::Route53::HostedZone::Id',
        'List<AWS::EC2::AvailabilityZone::Name>',
        'List<AWS::EC2::Image::Id>',
        'List<AWS::EC2::Instance::Id>',
        'List<AWS::EC2::SecurityGroup::GroupName>',
        'List<AWS::EC2::SecurityGroup::Id>',
        'List<AWS::EC2::Subnet::Id>',
        'List<AWS::EC2::Volume::Id>',
        'List<AWS::EC2::VPC::Id>',
        'List<AWS::Route53::HostedZone::Id>',
        'AWS::SSM::Parameter::Name'
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
