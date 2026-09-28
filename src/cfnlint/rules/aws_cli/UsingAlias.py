"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class UsingAlias(CloudFormationLintRule):
    id = "W1101"
    shortdesc = "Validate if the template is using YAML aliases"
    description = (
        "The CloudFormation service does not support YAML anchors or "
        "aliases. Templates that use them can only be deployed through the "
        "AWS CLI 'package' command or AWS SAM, which resolve the aliases "
        "client-side before sending the template to CloudFormation."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-formats.html"
    tags = ["yaml"]

    def match(self, cfn: Template):
        # SAM templates are deployed with the SAM CLI, which resolves the
        # aliases client-side
        if cfn.has_serverless_transform():
            return []

        # The YAML decoder records every alias with its own location.  The
        # decoded template can't be used to find them: an aliased scalar is
        # indistinguishable from a literal one.
        return [
            RuleMatch(
                path=alias.path,
                message=(
                    f"YAML alias '*{alias.name}' is rejected by CloudFormation "
                    "unless the template is first processed by the 'package' "
                    "cli command or AWS SAM"
                ),
                location=(
                    alias.start_mark.line,
                    alias.start_mark.column,
                    alias.end_mark.line,
                    alias.end_mark.column,
                ),
            )
            for alias in cfn.yaml_aliases
        ]
