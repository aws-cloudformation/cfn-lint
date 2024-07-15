"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class RefResolved(CloudFormationLintRule):
    id = "W1030"
    shortdesc = "Validate the values that come from a Ref function"
    description = "Resolve the Ref and then validate the values against the schema"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html"
    tags = ["functions", "ref"]
