"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import networkx

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class AccountsCreatedSequentially(CloudFormationLintRule):
    """Check that AWS::Organizations::Account resources are created one at a time"""

    id = "E3727"
    shortdesc = "Validate AWS Organizations accounts are created sequentially"
    description = (
        "AWS Organizations returns an error when more than one account is "
        "created at the same time, and the stack operation fails. When a "
        "template has more than one AWS::Organizations::Account resource, "
        "each account has to depend on the others (with DependsOn, Ref, "
        "Fn::GetAtt or Fn::Sub) so that CloudFormation creates them one after "
        "another."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-organizations-account.html"
    tags = ["resources", "organizations", "dependson"]

    def _can_exist_together(self, cfn: Template, names: list[str]) -> bool:
        conditions: dict[str, set[bool]] = {}
        for name in names:
            condition = cfn.template["Resources"][name].get("Condition")
            if isinstance(condition, str):
                conditions[condition] = {True}

        if not conditions:
            return True

        for _ in cfn.conditions.build_scenarios(conditions):
            return True

        return False

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []

        if cfn.graph is None:
            return matches

        graph = cfn.graph.graph
        accounts = [
            name
            for name in cfn.get_resources(["AWS::Organizations::Account"])
            if name in graph
        ]

        for index, account in enumerate(accounts):
            concurrent = []
            for other in accounts[:index]:
                if networkx.has_path(graph, account, other) or networkx.has_path(
                    graph, other, account
                ):
                    continue
                if not self._can_exist_together(cfn, [account, other]):
                    continue
                concurrent.append(other)

            if concurrent:
                others = ", ".join(repr(other) for other in concurrent)
                matches.append(
                    RuleMatch(
                        ["Resources", account],
                        (
                            f"AWS::Organizations::Account {account!r} can be "
                            f"created at the same time as {others}. Add a "
                            "DependsOn so the accounts are created one at a "
                            "time"
                        ),
                    )
                )

        return matches
