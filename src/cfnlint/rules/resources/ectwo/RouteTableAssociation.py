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


class RouteTableAssociation(CloudFormationLintRule):
    """Check only one route table association defined per subnet"""
    id = 'E3022'
    shortdesc = 'Resource SubnetRouteTableAssociation Properties'
    description = 'Validate there is only one SubnetRouteTableAssociation per subnet'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html'
    tags = ['resources', 'subnet', 'route table']

    def match(self, cfn):
        """Check SubnetRouteTableAssociation Resource Properties"""
        matches = []
        subnets = set()

        # Get all SubnetRouteTableAssociation resources from template
        resources = cfn.get_resources(['AWS::EC2::SubnetRouteTableAssociation'])
        for resource_name, resource in resources.items():
            properties = resource.get('Properties')
            print("Found rtAssociation: %s" % resource_name)
            if properties:
                subnetid = properties.get('SubnetId')
                if isinstance(subnetid, dict):
                    print("it's a dict!")
                    if len(subnetid) == 1:
                        for key, value in subnetid.items():
                            if key == 'Ref':
                                print("Found ref to: %s" % value)
                                subnetid = value
                print("SubnetId: %s" % subnetid)
                if subnetid in subnets:
                    path = ['Resources', resource_name, 'Properties', 'SubnetId']
                    message = 'Only one route table association is allowed per Subnet for {0}'
                    matches.append(
                        RuleMatch(path, message.format(resource_name)))
                else:
                    subnets.add(subnetid)

        return matches
