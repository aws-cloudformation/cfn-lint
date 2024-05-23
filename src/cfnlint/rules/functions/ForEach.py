"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template

LOGGER = logging.getLogger("cfnlint")


class ForEach(CloudFormationLintRule):
    id = "E1032"
    shortdesc = "Validates ForEach functions"
    description = "Validates that ForEach parameters have a valid configuration"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "foreach"]

    def validate_transform_is_declared(
        self, has_language_extensions_transform, tree, intrinsic_function
    ):
        matches = []
        if not has_language_extensions_transform:
            message = (
                "Missing Transform: Declare the AWS::LanguageExtensions Transform"
                " globally to enable use of the intrinsic function "
                + intrinsic_function
                + " at {0}"
            )
            matches.append(RuleMatch(tree[:], message.format("/".join(map(str, tree)))))
        return matches

    # pylint: disable=unused-argument
    def match(self, cfn: Template) -> RuleMatches:
        matches = []
        intrinsic_function = "Fn::ForEach"
        for_eaches = cfn.transform_pre["Fn::ForEach"]

        for for_each in for_eaches:
            has_language_extensions_transform = cfn.has_language_extensions_transform()

            matches.extend(
                self.validate_transform_is_declared(
                    has_language_extensions_transform,
                    for_each[:-1],
                    intrinsic_function,
                )
            )

        return matches
