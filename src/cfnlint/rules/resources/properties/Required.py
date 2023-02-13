"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
<<<<<<< HEAD

import cfnlint.helpers
from cfnlint.rules import CloudFormationLintRule, RuleMatch
=======
from cfnlint.rules import CloudFormationLintRule
>>>>>>> 91359e6d4 (Convert to using CloudFormation provider schemas)


class Required(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3003"
    shortdesc = "Required Resource properties are missing"
    description = "Making sure that Resources properties that are required exist"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#required"
    tags = ["resources"]
