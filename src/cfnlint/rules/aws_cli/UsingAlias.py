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
        matches: list[RuleMatch] = []
        # A YAML alias resolves to a single object referenced from more than
        # one place, so the template is a DAG.  Track visited object ids to
        # (a) detect the shared (aliased) nodes and (b) avoid re-walking them,
        # which would be exponential for nested aliases.
        seen: set[int] = set()
        reported: set[int] = set()
        # Iterative walk to avoid recursion limits on deeply nested templates.
        stack: list[tuple[object, list[str | int]]] = [(cfn.template, [])]
        while stack:
            obj, path = stack.pop()
            if not isinstance(obj, (dict, list)):
                continue
            obj_id = id(obj)
            if obj_id in seen:
                if obj_id not in reported:
                    reported.add(obj_id)
                    matches.append(
                        RuleMatch(
                            path=path,
                            message=(
                                "This code is using a YAML alias and can only "
                                "be deployed using the 'package' cli command "
                                "or AWS SAM"
                            ),
                        )
                    )
                continue
            seen.add(obj_id)
            if isinstance(obj, dict):
                for k, v in reversed(list(obj.items())):
                    stack.append((v, path + [k]))
            else:
                for i in range(len(obj) - 1, -1, -1):
                    stack.append((obj[i], path + [i]))
        return matches
