"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules import CloudFormationLintRule


class IfUnsatisfiable(CloudFormationLintRule):
    id = "W1028"
    shortdesc = "Check Fn::If has a path that cannot be reached"
    description = "Check Fn::If path can be reached"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-if"
    tags = ["functions", "if"]
