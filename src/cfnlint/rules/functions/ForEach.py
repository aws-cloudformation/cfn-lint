"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging

from cfnlint.languageExtensions import LanguageExtensions
from cfnlint.rules import CloudFormationLintRule

LOGGER = logging.getLogger("cfnlint")


class ForEach(CloudFormationLintRule):
    id = "E1032"
    shortdesc = "Validates ForEach functions"
    description = "Validates that ForEach parameters have a valid configuration"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "foreach"]

    # pylint: disable=unused-argument
    def match(self, cfn):
        matches = []
        intrinsic_function = "Fn::ForEach"
        for_eaches = cfn.transform_pre["Fn::ForEach"]

        for for_each in for_eaches:
            has_language_extensions_transform = cfn.has_language_extensions_transform()

            LanguageExtensions.validate_transform_is_declared(
                self,
                has_language_extensions_transform,
                matches,
                for_each[:-1],
                intrinsic_function,
            )

        return matches
