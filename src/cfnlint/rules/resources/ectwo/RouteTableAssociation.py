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
import cfnlint.helpers


class RouteTableAssociation(CloudFormationLintRule):
    """Check only one route table association defined per subnet"""
    id = 'E3022'
    shortdesc = 'Resource SubnetRouteTableAssociation Properties'
    description = 'Validate there is only one SubnetRouteTableAssociation per subnet'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html'
    tags = ['resources', 'subnet', 'route table']

    subnets = set()

    def check_value(self, subnetid, condition, resource_name):
        """Check subnet is not associated with other Route Tables"""
        matches = []
        values = self.get_values(subnetid, condition)
        for value in values:
            if '::' in value:
                (condition, bare_value) = value.split('::')
            else:
                bare_value = value
            if value in self.subnets or bare_value in self.subnets:
                path = ['Resources', resource_name, 'Properties', 'SubnetId']
                message = 'SubnetId is associated with another route table for {0}'
                matches.append(
                    RuleMatch(path, message.format(resource_name)))
            self.subnets.add(value)

        return matches

    def get_values(self, subnetid, condition):
        """Get string literal(s) from value of SubnetId"""
        values = []
        if isinstance(subnetid, dict):
            if len(subnetid) == 1:
                for key, value in subnetid.items():
                    if key in cfnlint.helpers.CONDITION_FUNCTIONS:
                        if isinstance(value, list):
                            if len(value) == 3:
                                condition = value[0]
                                values.extend(self.get_values(value[1], condition))
                                values.extend(self.get_values(value[2], condition))
                    if key in ('Ref', 'GetAtt'):
                        values.extend(self.get_values(value, condition))
        else:
            if condition:
                values.append(condition + '::' + subnetid)
            else:
                values.append(subnetid)
        return values

    def match(self, cfn):
        """Check SubnetRouteTableAssociation Resource Properties"""
        matches = []

        # Get all SubnetRouteTableAssociation resources from template
        resources = cfn.get_resources(['AWS::EC2::SubnetRouteTableAssociation'])
        for resource_name, resource in resources.items():
            properties = resource.get('Properties')
            condition = resource.get('Condition')
            if properties:
                subnetid = properties.get('SubnetId')
                matches.extend(
                    self.check_value(subnetid, condition, resource_name)
                )

        return matches
