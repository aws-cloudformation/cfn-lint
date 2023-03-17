"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class CfnRegionalSchema(CloudFormationLintRule):
    """Check additional schemas against a set of properties"""

    id = "E3018"
    shortdesc = "Properties are validated against additional schemas based on region"
    description = "Use supplemental JSON schemas to validate properties against"
    tags = ["resources"]
