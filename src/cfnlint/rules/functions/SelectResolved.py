"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class SelectResolved(CloudFormationLintRule):
    id = "W1035"
    shortdesc = "Validate the values that come from a Fn::Select function"
    description = (
        "Resolve the Fn::Select and then validate the values against the schema"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html"
    tags = ["functions", "select"]
