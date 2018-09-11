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
    id = 'W2508'
    shortdesc = 'Availability Zone Parameters are of correct type AWS::EC2::AvailabilityZone::Name'
    description = 'Check if a parameter is being used in a resource for Security ' \
                  'Group.  If it is make sure it is of type AWS::EC2::AvailabilityZone::Name'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters', 'availabilityzone']

    def __init__(self):
        """Init"""
        self.multiple_resource_type_specs = [
            'AWS::DAX::Cluster',
            'AWS::AutoScaling::AutoScalingGroup',
            'AWS::RDS::DBCluster',
            'AWS::ElasticLoadBalancing::LoadBalancer',
        ]

        self.singular_resource_type_specs = [
            'AWS::OpsWorks::Instance',
            'AWS::RDS::DBInstance',
            'AWS::EC2::Host',
            'AWS::DMS::ReplicationInstance',
            'AWS::EC2::Instance'
        ]

        self.singular_property_type_specs = [
            # Singular
            'AWS::EC2::LaunchTemplate.Placement',
            'AWS::EC2::SpotFleet.SpotPlacement',
            'AWS::EMR::Cluster.PlacementType',
            'AWS::Glue::Connection.PhysicalConnectionRequirements',
            'AWS::ElasticLoadBalancingV2::TargetGroup.TargetDescription',
            'AWS::EC2::SpotFleet.LaunchTemplateOverrides',
        ]

        for resoruce_type_spec in self.singular_resource_type_specs:
            self.resource_property_types.append(resoruce_type_spec)
        for resoruce_type_spec in self.multiple_resource_type_specs:
            self.resource_property_types.append(resoruce_type_spec)
        for property_type_spec in self.singular_property_type_specs:
            self.resource_sub_property_types.append(property_type_spec)

    # pylint: disable=W0613
    def check_az_ref(self, value, path, parameters, resources):
        """Check ref for VPC"""
        matches = []
        if 'AvailabilityZone' in path:
            allowed_types = [
                'AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>',
                'AWS::EC2::AvailabilityZone::Name'
            ]
        elif isinstance(path[-2], int):
            allowed_types = [
                'AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>',
                'AWS::EC2::AvailabilityZone::Name'
            ]
        else:
            allowed_types = [
                'AWS::SSM::Parameter::Value<List<AWS::EC2::AvailabilityZone::Name>>',
                'List<AWS::EC2::AvailabilityZone::Name>'
            ]

        if value in parameters:
            parameter_properties = parameters.get(value)
            parameter_type = parameter_properties.get('Type')
            if parameter_type not in allowed_types:
                path_error = ['Parameters', value, 'Type']
                message = 'Availability Zone Parameter should be of type [{0}] for {1}'
                matches.append(
                    RuleMatch(
                        path_error,
                        message.format(
                            ', '.join(map(str, allowed_types)),
                            '/'.join(map(str, path_error)))))

        return matches

    def check(self, properties, resource_type, path, cfn):
        """Check itself"""
        matches = []

        matches.extend(
            cfn.check_value(
                properties, 'AvailabilityZone', path,
                check_value=None, check_ref=self.check_az_ref,
                check_find_in_map=None, check_split=None, check_join=None
            )
        )
        matches.extend(
            cfn.check_value(
                properties, 'AvailabilityZones', path,
                check_value=None, check_ref=self.check_az_ref,
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
