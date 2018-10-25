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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
import cfnlint.helpers


class RouteTableAssociation(CloudFormationLintRule):
    """Check only one route table association defined per subnet"""
    id = 'E3022'
    shortdesc = 'Resource SubnetRouteTableAssociation Properties'
    description = 'Validate there is only one SubnetRouteTableAssociation per subnet'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html'
    tags = ['resources', 'subnet', 'route table']

    # Namespace for unique associated subnets in the form condition::value
    associated = set()

    def get_values(self, subnetid, resource_condition, property_condition):
        """Get string literal(s) from value of SubnetId"""
        values = []
        if isinstance(subnetid, dict):
            if len(subnetid) == 1:
                for key, value in subnetid.items():
                    if key in cfnlint.helpers.CONDITION_FUNCTIONS:
                        if isinstance(value, list):
                            if len(value) == 3:
                                property_condition = value[0]
                                values.extend(self.get_values(value[1], resource_condition, property_condition))
                                values.extend(self.get_values(value[2], resource_condition, property_condition))
                    if key == 'Ref':
                        values.extend(self.get_values(value, resource_condition, property_condition))
                    if key == 'Fn::GetAtt':
                        if isinstance(value[1], (six.string_types)):
                            sub_value = '.'.join(value)
                            values.append((resource_condition, property_condition, sub_value))
        else:
            values.append((resource_condition, property_condition, subnetid))
        return values

    def check_values(self, subnetid, resource_condition, resource_name):
        """Check subnet value is not associated with other route tables"""
        matches = []
        property_condition = None
        values = self.get_values(subnetid, resource_condition, property_condition)
        for value in values:
            print("%s : %s : %s" % (resource_name, value, self.associated))
            bare_value = (None, None, value[2])
            if value in self.associated or bare_value in self.associated:
                path = ['Resources', resource_name, 'Properties', 'SubnetId']
                message = 'SubnetId is associated with another route table for {0}'
                matches.append(
                    RuleMatch(path, message.format(resource_name)))
            self.associated.add(value)
            self.associated.add((None, None, value[2]))

        return matches

    def match(self, cfn):
        """Check SubnetRouteTableAssociation Resource Properties"""
        matches = []

        resources = cfn.get_resources(['AWS::EC2::SubnetRouteTableAssociation'])
        for resource_name, resource in resources.items():
            properties = resource.get('Properties')
            if properties:
                resource_condition = resource.get('Condition')
                subnetid = properties.get('SubnetId')
                matches.extend(
                    self.check_values(subnetid, resource_condition, resource_name)
                )

        return matches
