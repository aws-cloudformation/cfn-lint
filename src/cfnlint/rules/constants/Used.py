"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import unicode_literals

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class Used(CloudFormationLintRule):
    """Check if Constants are used"""

    id = "W9003"
    shortdesc = "Check if Constants are Used"
    description = "Making sure the constants defined are used"
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["constants"]

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []
        
        # Constants only work with LanguageExtensions transform
        if not cfn.has_language_extensions_transform():
            return matches

        constants = cfn.template.get("Constants", {})
        if not constants:
            return matches

        # Get all Refs
        refs = []
        reftrees = cfn.search_deep_keys("Ref")
        for reftree in reftrees:
            refs.append(reftree[-1])

        # Get all Fn::Sub parameters
        subs = []
        subtrees = cfn.search_deep_keys("Fn::Sub")
        for subtree in subtrees:
            if isinstance(subtree[-1], list):
                subs.extend(cfn.get_sub_parameters(subtree[-1][0]))
            elif isinstance(subtree[-1], str):
                subs.extend(cfn.get_sub_parameters(subtree[-1]))

        # Check if each constant is used
        for constant_name in constants.keys():
            if constant_name not in refs and constant_name not in subs:
                message = "Constant {0} not used."
                matches.append(
                    RuleMatch(
                        ["Constants", constant_name],
                        message.format(constant_name),
                    )
                )

        return matches
