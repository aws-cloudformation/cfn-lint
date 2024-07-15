"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class SplitResolved(CloudFormationLintRule):
    id = "W1033"
    shortdesc = "Validate the values that come from a Fn::Split function"
    description = (
        "Resolve the Fn::Split and then validate the values against the schema"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-split.html"
    tags = ["functions", "split"]
