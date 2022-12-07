"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class EqualsIsUseful(CloudFormationLintRule):
    """Validate that the Equals will return true/false and not always be true or false"""

    id = "W8003"
    shortdesc = "Fn::Equals will always return true or false"
    description = "Validate Fn::Equals to see if its comparing two strings or two equal items. While this works it may not be intended."
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-equals"
    tags = ["functions", "equals"]

    function = "Fn::Equals"

    def _check_equal_values(self, values, path):
        matches = []

        if json.dumps(values[0]) == json.dumps(values[1]):
            message = self.function + " element will alway return true"
            matches.append(RuleMatch(path, message))
        elif isinstance(values[0], str) and isinstance(values[1], str):
            message = self.function + " element will alway return false"
            matches.append(RuleMatch(path, message))
        return matches

    def match(self, cfn):
        matches = []
        # Build the list of functions
        trees = cfn.search_deep_keys(self.function)

        for tree in trees:
            # Test when in Conditions
            if tree[0] == "Conditions":
                value = tree[-1]
                if isinstance(value, list) and len(value) == 2:
                    matches.extend(self._check_equal_values(value, tree[:-1]))

        return matches
