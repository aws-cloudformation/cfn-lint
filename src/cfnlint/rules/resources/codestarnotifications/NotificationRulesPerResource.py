"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from itertools import islice
from typing import Any

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template

# Most condition scenarios to check before giving up
_MAX_SCENARIOS = 1024


class NotificationRulesPerResource(CloudFormationLintRule):
    """Check the number of notification rules for a resource"""

    id = "E3731"
    shortdesc = "Validate the number of notification rules for a resource"
    description = (
        "AWS CodeStar Notifications allows at most 10 notification rules for "
        "a resource. Combine the events and targets into fewer "
        "AWS::CodeStarNotifications::NotificationRule resources, as one rule "
        "can have many event types and up to 10 targets"
    )
    source_url = "https://docs.aws.amazon.com/dtconsole/latest/userguide/limits.html"
    tags = ["resources", "codestarnotifications", "limits"]

    _limit = 10

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []

        # Group the notification rules by the resource they are for
        groups: dict[str, list[str]] = {}
        for name, resource in cfn.get_resources(
            ["AWS::CodeStarNotifications::NotificationRule"]
        ).items():
            properties = resource.get("Properties")
            if not isinstance(properties, dict):
                continue
            source = properties.get("Resource")
            if source is None:
                continue
            key = json.dumps(source, sort_keys=True, default=str)
            groups.setdefault(key, []).append(name)

        resources = cfn.get_resources()
        for names in groups.values():
            if len(names) <= self._limit:
                continue

            count = self._max_rules(cfn, names, resources)
            if count is None or count <= self._limit:
                continue

            name = names[self._limit]
            matches.append(
                RuleMatch(
                    ["Resources", name, "Properties", "Resource"],
                    (
                        f"Up to {count} notification rules exist at the same "
                        f"time for one resource ({', '.join(names)}), more "
                        f"than the limit of {self._limit}. Combine their "
                        "events and targets into fewer notification rules"
                    ),
                )
            )

        return matches

    def _max_rules(
        self, cfn: Template, names: list[str], resources: dict[str, Any]
    ) -> int | None:
        """The most of these rules that can exist at the same time, or None
        if it can't be worked out"""
        conditions: dict[str, set[bool]] = {}
        for name in names:
            condition = resources[name].get("Condition")
            if condition is None:
                continue
            if not isinstance(condition, str):
                return None
            conditions[condition] = {True, False}

        if not conditions:
            return len(names)

        scenarios = list(
            islice(cfn.conditions.build_scenarios(conditions), _MAX_SCENARIOS + 1)
        )
        if len(scenarios) > _MAX_SCENARIOS:
            return None

        best = 0
        for scenario in scenarios:
            count = sum(
                1
                for name in names
                if scenario.get(resources[name].get("Condition"), True)
            )
            best = max(best, count)
        return best
