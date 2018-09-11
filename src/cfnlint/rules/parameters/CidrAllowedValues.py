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

from cfnlint.helpers import REGEX_CIDR


class CidrAllowedValues(CloudFormationLintRule):
    """Check Availability Zone parameter checks """
    id = 'E2004'
    shortdesc = 'CIDR Allowed Values should be a Cidr Range'
    description = 'Check if a parameter is being used as a CIDR. ' \
                  'If it is make sure allowed values are proper CIDRs'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters', 'cidr']

    def __init__(self):
        """Init"""
        resource_type_specs = [
            'AWS::EC2::Subnet',
            'AWS::EC2::Vpc',
            'AWS::RDS::DBSecurityGroupIngress',
            'AWS::EC2::NetworkAclEntry',
            'AWS::EC2::SecurityGroupIngress',
            'AWS::EC2::SecurityGroupEgress',
            'AWS::Redshift::ClusterSecurityGroupIngress',
            'AWS::EC2::VPCCidrBlock',
        ]

        property_type_specs = [
            'AWS::RDS::DBSecurityGroup.Ingress',
            'AWS::EC2::SecurityGroup.Egress',
            'AWS::SES::ReceiptFilter.IpFilter',
            'AWS::EC2::SecurityGroup.Ingress',
        ]

        for resource_type_spec in resource_type_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in property_type_specs:
            self.resource_sub_property_types.append(property_type_spec)

    # pylint: disable=W0613
    def check_cidr_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = []

        if value in parameters:
            parameter = parameters.get(value, {})
            allowed_values = parameter.get('AllowedValues', None)
            if allowed_values:
                for cidr in allowed_values:
                    if not re.match(REGEX_CIDR, cidr):
                        cidr_path = ['Parameters', value]
                        message = 'Cidr should be a Cidr Range based string for {0}'
                        matches.append(RuleMatch(cidr_path, message.format(cidr)))

        return matches

    def check(self, properties, resource_type, path, cfn):
        """Check itself"""
        matches = []

        matches.extend(
            cfn.check_value(
                properties, 'CIDRIP', path,
                check_value=None, check_ref=self.check_cidr_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'Cidr', path,
                check_value=None, check_ref=self.check_cidr_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'CidrBlock', path,
                check_value=None, check_ref=self.check_cidr_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'CidrIp', path,
                check_value=None, check_ref=self.check_cidr_ref,
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
