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


class ImportValue(CloudFormationLintRule):
    """Check if a Output is done of another output"""
    id = 'W6001'
    shortdesc = 'Check Outputs using ImportValue'
    description = 'Check if the Output value is set using ImportValue, so creating an Output of an Output'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['outputs', 'importvalue']

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        # Get all import values
        importvalue_trees = cfn.search_deep_keys('Fn::ImportValue')

        # Filter out the Outputs
        importvalue_trees = [x for x in importvalue_trees if x[0] == 'Outputs']

        # Check if the importvalue is set on the Value
        for importvalue_tree in importvalue_trees:
            # Skip invalid configuration, let other rules handle that
            if len(importvalue_tree) < 4:
                continue

            if importvalue_tree[2] == 'Value':
                # ImportValue can be used within other intrinic function, exclude those
                if importvalue_tree[3] == 'Fn::ImportValue':
                    message = 'The value of output ({0}) is imported from another output ({1})'
                    matches.append(RuleMatch(importvalue_tree, message.format(importvalue_tree[1], importvalue_tree[-1])))

        return matches
