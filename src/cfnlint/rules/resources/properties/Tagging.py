"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class UniqueNames(CloudFormationLintRule):
    id = "E3021"
    shortdesc = "Validate tag configuration"
    description = (
        "Validates tag values to make sure they have unique keys "
        "and they follow pattern requirements"
    )
    source_url = "https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html"
    tags = ["parameters", "resources", "tags"]
