"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class ImportValue(CloudFormationLintRule):
    """Check if a Output is done of another output"""
    id = 'W6001'
    shortdesc = 'Check Outputs using ImportValue'
    description = 'Check if the Output value is set using ImportValue, so creating an Output of an Output'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['outputs', 'importvalue']

    def match(self, cfn):
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
                    matches.append(RuleMatch(importvalue_tree, message.format(
                        importvalue_tree[1], importvalue_tree[-1])))

        return matches
