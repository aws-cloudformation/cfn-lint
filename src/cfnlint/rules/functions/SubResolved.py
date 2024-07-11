"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class SubResolved(CloudFormationLintRule):
    id = "W1031"
    shortdesc = "Validate the values that come from a Fn::Sub function"
    description = "Resolve the Fn::Sub and then validate the values against the schema"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html"
    tags = ["functions", "sub"]
