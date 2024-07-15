"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class FindInMapResolved(CloudFormationLintRule):
    id = "W1036"
    shortdesc = "Validate the values that come from a Fn::GetAZs function"
    description = (
        "Resolve the Fn::GetAZs and then validate the values against the schema"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getavailabilityzones.html"
    tags = ["functions", "getazs"]
