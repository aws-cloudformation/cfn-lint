"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class JoinResolved(CloudFormationLintRule):
    id = "W1032"
    shortdesc = "Validate the values that come from a Fn::Join function"
    description = "Resolve the Fn::Join and then validate the values against the schema"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-join.html"
    tags = ["functions", "join"]
