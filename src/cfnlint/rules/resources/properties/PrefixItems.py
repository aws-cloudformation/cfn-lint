"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule


class PrefixItems(CloudFormationLintRule):
    """Check Required Resource Configuration"""

    id = "E3008"
    shortdesc = "Validate an array in order"
    description = "Will validate arrays in order for schema validation"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#prefixitems"
    tags = ["resources", "properties", "array", "prefixItems"]
