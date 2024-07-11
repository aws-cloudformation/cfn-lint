"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class ToJsonStringResolved(CloudFormationLintRule):
    id = "W1040"
    shortdesc = "Validate the values that come from a Fn::ToJsonString function"
    description = (
        "Resolve the Fn::ToJsonString and then validate the values against the schema"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ToJsonString.html"
    tags = ["functions", "tojsonstring"]
