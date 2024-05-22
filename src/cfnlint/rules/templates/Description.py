"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class Description(CloudFormationLintRule):
    """Check Template Description is only a String"""

    id = "E1004"
    shortdesc = "Template description can only be a string"
    description = "Template description can only be a string"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-description-structure.html"
    tags = ["description"]

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []

        description = cfn.template.get("Description")
        if "Description" not in cfn.template:
            return matches

        if not isinstance(description, str):
            message = "Description can only be a string"
            matches.append(RuleMatch(["Description"], message))
        return matches
