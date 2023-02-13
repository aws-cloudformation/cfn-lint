"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class RequiredBasedOnValue(CloudFormationLintRule):
    """Check additional schemas against a set of properties"""

    id = "E3017"
    shortdesc = "Properties are validated against additional schemas"
    description = "Use supplemental JSON schemas to validate properties against"
    tags = ["resources"]
