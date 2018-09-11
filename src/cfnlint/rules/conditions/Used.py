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


class Used(CloudFormationLintRule):
    """Check if Conditions are configured correctly"""
    id = 'W8001'
    shortdesc = 'Check if Conditions are Used'
    description = 'Making sure the conditions defined are used'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['conditions']

    def match(self, cfn):
        """Check CloudFormation Conditions"""

        matches = []
        ref_conditions = []

        conditions = cfn.template.get('Conditions', {})
        if conditions:
            # Get all "If's" that reference a Condition
            iftrees = cfn.search_deep_keys('Fn::If')

            for iftree in iftrees:
                if isinstance(iftree[-1], list):
                    ref_conditions.append(iftree[-1][0])
                else:
                    ref_conditions.append(iftree[-1])
            # Get resource's Conditions
            for _, resource_values in cfn.get_resources().items():
                if 'Condition' in resource_values:
                    ref_conditions.append(resource_values['Condition'])

            # Get conditions used by another condition
            condtrees = cfn.search_deep_keys('Condition')

            for condtree in condtrees:
                if condtree[0] == 'Conditions':
                    if isinstance(condtree[-1], (str, six.text_type, six.string_types)):
                        ref_conditions.append(condtree[-1])

            # Get resource's Conditions
            for _, resource_values in cfn.get_resources().items():
                if 'Condition' in resource_values:
                    ref_conditions.append(resource_values['Condition'])

            # Get Output Conditions
            for _, output_values in cfn.template.get('Outputs', {}).items():
                if 'Condition' in output_values:
                    ref_conditions.append(output_values['Condition'])

            # Check if the confitions are used
            for condname, _ in conditions.items():
                if condname not in ref_conditions:
                    message = 'Condition {0} not used'
                    matches.append(RuleMatch(
                        ['Conditions', condname],
                        message.format(condname)
                    ))

        return matches
