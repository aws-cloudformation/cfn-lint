"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

from cfnlint.helpers import REGEX_CIDR


class CidrAllowedValues(CloudFormationLintRule):
    """CIDR checks"""
    id = 'E2004'
    shortdesc = 'CIDR Allowed Values should be a Cidr Range'
    description = 'Check if a parameter is being used as a CIDR. ' \
                  'If it is make sure allowed values are proper CIDRs'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters', 'cidr']

    def __init__(self):
        """Init"""
        super(CidrAllowedValues, self).__init__()
        resource_type_specs = [
            'AWS::EC2::ClientVpnAuthorizationRule',
            'AWS::EC2::ClientVpnEndpoint',
            'AWS::EC2::ClientVpnRoute',
            'AWS::EC2::NetworkAclEntry',
            'AWS::EC2::Route',
            'AWS::EC2::SecurityGroupEgress',
            'AWS::EC2::SecurityGroupIngress',
            'AWS::EC2::Subnet',
            'AWS::EC2::TransitGatewayRoute',
            'AWS::EC2::VPC',
            'AWS::EC2::VPCCidrBlock',
            'AWS::EC2::VPNConnectionRoute',
            'AWS::RDS::DBSecurityGroupIngress',
            'AWS::Redshift::ClusterSecurityGroupIngress',
        ]

        property_type_specs = [
            'AWS::EC2::SecurityGroup.Egress',
            'AWS::EC2::SecurityGroup.Ingress',
            'AWS::EC2::VPNConnection.VpnTunnelOptionsSpecification',
            'AWS::MediaLive::InputSecurityGroup.InputWhitelistRuleCidr',
            'AWS::RDS::DBSecurityGroup.Ingress',
            'AWS::SES::ReceiptFilter.IpFilter',
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

        for cidrString in [
                'CIDRIP',
                'Cidr',
                'CidrBlock',
                'CidrIp',
                'ClientCidrBlock',
                'DestinationCidrBlock',
                'TargetNetworkCidr',
                'TunnelInsideCidr',
        ]:
            matches.extend(
                cfn.check_value(
                    properties, cidrString, path,
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
