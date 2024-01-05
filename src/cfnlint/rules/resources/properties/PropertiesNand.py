"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class PropertiesNand(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3019"
    shortdesc = "Validate one or less properties are provided"
    description = "Making sure that required resource properties have just one or none"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#pr"
    tags = ["resources"]
