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


class IfExist(CloudFormationLintRule):
    """Check if Condition exists"""
    id = 'E1025'
    shortdesc = 'Check if Conditions exist'
    description = 'Making sure the Conditions used in Fn:If functions exist'
    tags = ['base', 'functions', 'if']

    def match(self, cfn):
        """Check CloudFormation Conditions"""

        matches = list()
        if_conditions = list()

        # Build the list of functions
        iftrees = cfn.search_deep_keys('Fn::If')

        # Get the conditions used in the functions
        for iftree in iftrees:
            if isinstance(iftree[-1], list):
                if_condition = iftree[-1][0]
            else:
                if_condition = iftree[-1]
            # Condations can be referenced multiple times, check them once
            if not if_condition in if_conditions:
                if_conditions.append(if_condition)

        conditions = cfn.template.get('Conditions', {})

        for if_condition in if_conditions:
            if if_condition not in conditions:
                message = 'Referenced condition {0} not specified'
                matches.append(RuleMatch(
                    ['Conditions', if_condition],
                    message.format(if_condition)
                ))

        return matches
