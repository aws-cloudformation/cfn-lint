"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class PropertiesNand(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3019"
    shortdesc = "Validate at none or only one property is provided"
    description = "Making sure that required resource properties have just one"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#pr"
    tags = ["resources"]
