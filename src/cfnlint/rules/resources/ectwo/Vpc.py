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
import re
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch

import cfnlint.helpers

class Vpc(CloudFormationLintRule):
    """Check if EC2 VPC Resource Properties"""
    id = 'E2505'
    shortdesc = 'Resource EC2 VPC Properties'
    description = 'Check if the default tenancy is default or dedicated and ' \
                  'that CidrBlock is a valid CIDR range.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html'
    tags = ['properties', 'vpc']

    def check_cidr_value(self, value, path):
        """Check CIDR Strings"""
        matches = []

        if not re.match(cfnlint.helpers.REGEX_CIDR, value):
            message = 'CidrBlock needs to be of x.x.x.x/y at {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(['Parameters', value])))))
        else:
            # CHeck the netmask block, has to be between /16 and /28
            netmask = int(value.split('/')[1])

            if netmask < 16 or netmask > 28:
                message = 'VPC Cidrblock netmask ({}) must be between /16 and /28'
                matches.append(RuleMatch(path, message.format(value)))

        return matches

    def check_cidr_ref(self, value, path, parameters, resources):
        """Check CidrBlock for VPC"""
        matches = []

        allowed_types = [
            'String',
            'AWS::SSM::Parameter::Value<String>',
        ]
        if value in resources:
            resource_obj = resources.get(value, {})
            if resource_obj:
                resource_type = resource_obj.get('Type', '')
                if not cfnlint.helpers.is_custom_resource(resource_type):
                    message = 'CidrBlock needs to be a valid Cidr Range at {0}'
                    matches.append(RuleMatch(path, message.format(('/'.join(['Parameters', value])))))
        if value in parameters:
            parameter = parameters.get(value, {})
            parameter_type = parameter.get('Type', None)
            if parameter_type not in allowed_types:
                path_error = ['Parameters', value, 'Type']
                message = 'CidrBlock parameter should be of type [{0}] for {1}'
                matches.append(
                    RuleMatch(
                        path_error,
                        message.format(
                            ', '.join(map(str, allowed_types)),
                            '/'.join(map(str, path_error)))))
        return matches

    def match(self, cfn):
        """Check EC2 VPC Resource Parameters"""

        matches = []
        matches.extend(
            cfn.check_resource_property(
                'AWS::EC2::VPC', 'CidrBlock',
                check_value=self.check_cidr_value,
                check_ref=self.check_cidr_ref,
            )
        )

        return matches
