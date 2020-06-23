"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class AvailabilityZone(CloudFormationLintRule):
    """Check Availibility Zone parameter checks """
    id = 'W3010'
    shortdesc = 'Availability Zone Parameters should not be hardcoded'
    description = 'Check if an Availability Zone property is hardcoded.'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['parameters', 'availabilityzone']

    def __init__(self):
        """Init"""
        super(AvailabilityZone, self).__init__()
        resource_type_specs = [
            'AWS::AutoScaling::AutoScalingGroup',
            'AWS::DAX::Cluster',
            'AWS::DMS::ReplicationInstance',
            'AWS::EC2::Host',
            'AWS::EC2::Instance',
            'AWS::EC2::Subnet',
            'AWS::EC2::Volume',
            'AWS::ElasticLoadBalancing::LoadBalancer',
            'AWS::OpsWorks::Instance',
            'AWS::RDS::DBCluster',
            'AWS::RDS::DBInstance',
        ]

        property_type_specs = [
            # Singular
            'AWS::EC2::LaunchTemplate.Placement',
            'AWS::EC2::SpotFleet.LaunchTemplateOverrides',
            'AWS::EC2::SpotFleet.SpotPlacement',
            'AWS::EMR::Cluster.PlacementType',
            'AWS::ElasticLoadBalancingV2::TargetGroup.TargetDescription',
            'AWS::Glue::Connection.PhysicalConnectionRequirements',
        ]

        for resource_type_spec in resource_type_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in property_type_specs:
            self.resource_sub_property_types.append(property_type_spec)

    # pylint: disable=W0613
    def check_az_value(self, value, path):
        matches = []

        # value of `all` is a valide exception in AWS::ElasticLoadBalancingV2::TargetGroup
        if value not in ['all']:
            if path[-1] != ['Fn::GetAZs']:
                message = 'Don\'t hardcode {0} for AvailabilityZones'
                matches.append(RuleMatch(path, message.format(value)))

        return matches

    def check(self, properties, resource_type, path, cfn):
        """Check itself"""
        matches = []

        matches.extend(
            cfn.check_value(
                properties, 'AvailabilityZone', path,
                check_value=self.check_az_value, check_ref=None,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'AvailabilityZones', path,
                check_value=self.check_az_value, check_ref=None,
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
