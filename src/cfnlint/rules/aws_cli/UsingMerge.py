"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class UsingMerge(CloudFormationLintRule):
    id = "W1100"
    shortdesc = "Validate if the template is using YAML merge"
    description = (
        "The CloudFormation service does not support YAML anchors, "
        "aliases, or merging. This rule validates if the "
        "merge capability is being used"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-formats.html"
    tags = ["yaml"]

    def _nested_obj(self, obj: Any, path: list[str | int]) -> list[RuleMatch]:
        matches = []
        if isinstance(obj, dict):
            if hasattr(obj, "using_merge") and obj.using_merge:
                matches.append(
                    RuleMatch(
                        path=path,
                        message=(
                            "This code is using yaml marge capabilities "
                            "and can only be deployed using the "
                            "'package' cli command"
                        ),
                    )
                )
            for k, v in obj.items():
                matches.extend(self._nested_obj(v, path + [k]))
        elif isinstance(obj, list):
            for i, e in enumerate(obj):
                matches.extend(self._nested_obj(e, path + [i]))
        return matches

    def match(self, cfn: Template):

        return self._nested_obj(cfn.template, [])
