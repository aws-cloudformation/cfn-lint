"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging

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
        return []
