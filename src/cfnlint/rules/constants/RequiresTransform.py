"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class RequiresTransform(CloudFormationLintRule):
    """Check that Constants section requires AWS::LanguageExtensions transform"""

    id = "E9002"
    shortdesc = "Constants requires AWS::LanguageExtensions transform"
    description = (
        "The Constants section can only be used when the template includes "
        "Transform: AWS::LanguageExtensions"
    )
    # TODO: Update source_url once Constants documentation is published
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html"
    tags = ["constants", "transform"]

    def match(self, cfn: Template):
        """Check CloudFormation template for Constants without
        LanguageExtensions transform"""
        matches: RuleMatches = []

        # Check if Constants section exists
        constants = cfn.template.get("Constants")
        if not constants:
            return matches

        # Check if AWS::LanguageExtensions transform is present
        transform = cfn.template.get("Transform")
        has_language_extensions = False
        
        if isinstance(transform, str):
            has_language_extensions = transform == "AWS::LanguageExtensions"
        elif isinstance(transform, list):
            has_language_extensions = "AWS::LanguageExtensions" in transform
        
        if not has_language_extensions:
            message = (
                "Constants section requires "
                "'Transform: AWS::LanguageExtensions' "
                "to be present in the template"
            )
            matches.append(
                RuleMatch(
                    ["Constants"],
                    message,
                )
            )

        return matches
