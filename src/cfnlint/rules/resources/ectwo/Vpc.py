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


class Vpc(CloudFormationLintRule):
    """Check if EC2 VPC Resource Properties"""
    id = 'E2505'
    shortdesc = 'Resource EC2 VPC Properties'
    description = 'See if EC2 VPC Properties are set correctly'
    tags = ['base', 'properties', 'vpc']

    # pylint: disable=C0301
    cidr_regex = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$'

    def check_vpc_value(self, value, path):
        """Check VPC Values"""
        matches = list()

        if value not in ('default', 'dedicated'):
            message = 'DefaultTenancy needs to be default or dedicated for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        return matches

    def check_vpc_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = list()
        if value in resources:
            message = 'DefaultTenancy can\'t use a Ref to a resource for {0}'
            matches.append(RuleMatch(path, message.format(('/'.join(path)))))
        elif value in parameters:
            parameter = parameters.get(value, {})
            allowed_values = parameter.get('AllowedValues', '')
            if allowed_values != ['default', 'dedicated']:
                message = 'AllowedValues for Parameter should be default or dedicated for {0}'
                matches.append(RuleMatch(path, message.format(('/'.join(['Parameters', value])))))
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

    def match(self, cfn):
        """Check EC2 VPC Resource Parameters"""

        matches = list()
        matches.extend(
            cfn.check_resource_property(
                'AWS::EC2::VPC', 'InstanceTenancy',
                check_value=self.check_vpc_value,
                check_ref=self.check_vpc_ref,
            )
        )
        matches.extend(
            cfn.check_resource_property(
                'AWS::EC2::VPC', 'CidrBlock',
                check_value=self.check_cidr_value,
                check_ref=self.check_cidr_ref,
            )
        )

        return matches
