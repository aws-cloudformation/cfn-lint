"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import unicode_literals

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class Used(CloudFormationLintRule):
    """Check if Parameters are used"""

    id = "W2001"
    shortdesc = "Check if Parameters are Used"
    description = "Making sure the parameters defined are used"
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["parameters"]

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []
        if cfn.transform_pre["Transform"]:
            return matches

        le_refs = None
        if cfn.has_language_extensions_transform():
            le_refs = cfn.search_deep_keys("Ref")

        reftrees = cfn.transform_pre.get("Ref", [])
        subtrees = cfn.transform_pre.get("Fn::Sub", [])
        refs = []
        for reftree in reftrees:
            refs.append(reftree[-1])
        if le_refs:
            for le_ref in le_refs:
                if le_ref[-1] not in refs:
                    refs.append(le_ref[-1])

        subs = []
        for subtree in subtrees:
            if isinstance(subtree[-1], list):
                subs.extend(cfn.get_sub_parameters(subtree[-1][0]))
            elif isinstance(subtree[-1], str):
                subs.extend(cfn.get_sub_parameters(subtree[-1]))

        for paramname in cfn.template.get("Parameters", {}).keys():
            if paramname not in refs:
                if paramname not in subs:
                    message = "Parameter {0} not used."
                    matches.append(
                        RuleMatch(["Parameters", paramname], message.format(paramname))
                    )

        return matches
