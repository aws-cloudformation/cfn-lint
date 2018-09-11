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


class AvailabilityZone(CloudFormationLintRule):
    """Check Availibility Zone parameter checks """
    id = 'W3010'
    shortdesc = 'Availability Zone Parameters should not be hardcoded'
    description = 'Check if an Availability Zone property is hardcoded.'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['parameters', 'availabilityzone']

    def __init__(self):
        """Init"""
        resource_type_specs = [
            'AWS::DAX::Cluster',
            'AWS::AutoScaling::AutoScalingGroup',
            'AWS::RDS::DBCluster',
            'AWS::ElasticLoadBalancing::LoadBalancer',
            'AWS::OpsWorks::Instance',
            'AWS::RDS::DBInstance',
            'AWS::EC2::Host',
            'AWS::DMS::ReplicationInstance',
            'AWS::EC2::Instance'
        ]

        property_type_specs = [
            # Singular
            'AWS::EC2::LaunchTemplate.Placement',
            'AWS::EC2::SpotFleet.SpotPlacement',
            'AWS::EMR::Cluster.PlacementType',
            'AWS::Glue::Connection.PhysicalConnectionRequirements',
            'AWS::ElasticLoadBalancingV2::TargetGroup.TargetDescription',
            'AWS::EC2::SpotFleet.LaunchTemplateOverrides',
        ]

        for resoruce_type_spec in resource_type_specs:
            self.resource_property_types.append(resoruce_type_spec)
        for property_type_spec in property_type_specs:
            self.resource_sub_property_types.append(property_type_spec)

    # pylint: disable=W0613
    def check_az_value(self, value, path):
        """Check ref for VPC"""
        matches = []

        if path[-1] != 'Fn::GetAZs':
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
