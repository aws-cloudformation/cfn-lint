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
from cfnlint.helpers import REGEX_ALPHANUMERIC


class TestRule(CloudFormationLintRule):
    """Check if Resources are named correctly"""
    id = 'E3006'
    shortdesc = 'Resources have appropriate names'
    description = 'Check if Resources are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html#resources-section-structure-logicalid'
    tags = ['resources']

    def match(self, cfn):
        """Check CloudFormation Mapping"""

        matches = []

        # scenarios = cfn.is_resource_available(
        #    ['Resources', 'myInstanceX2', 'Properties', 'BlockDeviceMappings', 'Fn::If', 2, 0, 'Fn::If', 1, 'VirtualName'],
        #    'mySubnet'
        # )

        # scenarios = cfn.get_condition_scenarios_from_paths([['Resources', 'myInstanceX2', 'Properties', 'BlockDeviceMappings', 'Fn::If', 2, 0, 'Fn::If', 1, 'VirtualName']])

        # scenarios = cfn.get_conditions_scenarios_from_object(cfn.template.get('Resources', {}).get('myInstanceX2', {}).get('Properties', {}).get('BlockDeviceMappings', {}))

        return matches

    # I want to get property sets for when conditions are used for values

    # To do this I need to know all the conditions directly in the value space
    # I need to know if the conditions are related to other conditions

    # Finding related conditions
    #  - this could be done by REFing the same parameter or same findinmap
    #  - or using the other condition in and, or or not
