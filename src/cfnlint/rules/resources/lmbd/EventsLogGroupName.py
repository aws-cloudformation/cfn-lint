"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class EventsLogGroupName(CloudFormationLintRule):
    """Check if the settings of multiple subscriptions are included for one LogGroup"""

    id = "E2529"
    shortdesc = (
        "Check for SubscriptionFilters have beyond 5 attachments to a CloudWatch Log"
        " Group"
    )
    description = (
        "The current limit for a CloudWatch Log Group is they can have 5 subscription"
        " filters. We will look for duplicate LogGroupNames inside Subscription Filters"
        " and make sure they are within 5. This doesn't account for any other"
        " subscription filters getting set. Filters gated by Conditions are counted"
        " per condition scenario, so filters that can never exist at the same time"
        " are not counted together."
    )
    source_url = "https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/cloudwatch_limits_cwl.html"
    tags = ["resources", "lambda"]
    limit = 5

    def check_events_subscription_duplicated(self, cfn: Template) -> RuleMatches:
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        message = (
            f"You can only have {self.limit} Subscription Filters per CloudWatch Log"
            " Group"
        )

        log_group_paths = self.__get_log_group_name_list(cfn)
        for _, entries in log_group_paths.items():
            path = self.__get_limit_exceeding_path(cfn, entries)
            if path is not None:
                matches.append(RuleMatch(path, message))

        return matches

    def __get_limit_exceeding_path(
        self,
        cfn: Template,
        entries: list[tuple[list[str | int], str | None]],
    ) -> list[str | int] | None:
        """Return the path of the first filter over the limit, if any.

        Filters without a Condition exist in every scenario. Filters with a
        Condition exist only in scenarios where that Condition is true, so
        the count that matters is the largest count over all satisfiable
        condition scenarios, not the flat total. When the Conditions cannot
        be resolved (for example an undefined Condition name) fall back to
        the flat total so the rule keeps reporting instead of going silent.
        """
        conditions = {condition for _, condition in entries if condition}
        if not conditions:
            if len(entries) > self.limit:
                return entries[self.limit][0]
            return None

        scenarios = list(
            cfn.conditions.build_scenarios({name: {True, False} for name in conditions})
        )
        if not scenarios:
            if len(entries) > self.limit:
                return entries[self.limit][0]
            return None

        worst: list[list[str | int]] = []
        for scenario in scenarios:
            present = [
                path
                for path, condition in entries
                if condition is None or scenario.get(condition, True)
            ]
            if len(present) > len(worst):
                worst = present

        if len(worst) > self.limit:
            return worst[self.limit]
        return None

    def __get_log_group_name_list(
        self,
        cfn: Template,
    ) -> dict[str, list[tuple[list[str | int], str | None]]]:
        log_group_paths: dict[str, list[tuple[list[str | int], str | None]]] = {}

        # Enumerate AWS::Logs::SubscriptionFilter resources
        for resource_name, resource in cfn.get_resources(
            "AWS::Logs::SubscriptionFilter"
        ).items():
            prop = resource.get("Properties")
            if not isinstance(prop, dict):
                continue
            log_group_name = json.dumps(prop.get("LogGroupName"))

            if log_group_name not in log_group_paths:
                log_group_paths[log_group_name] = []

            log_group_paths[log_group_name].append(
                (
                    ["Resources", resource_name, "Properties", "LogGroupName"],
                    self.__get_condition(resource),
                ),
            )

        # Enumerate AWS::Serverless::Function CloudWatchLogs events
        for resource_name, resource in cfn.get_resources(
            "AWS::Serverless::Function"
        ).items():
            props = resource.get("Properties")
            if not isinstance(props, dict):
                continue
            events = props.get("Events")
            if not isinstance(events, dict):
                continue

            for event_id, event in events.items():
                if not isinstance(event, dict):
                    continue
                if event.get("Type") != "CloudWatchLogs":
                    continue
                event_props = event.get("Properties")
                if not isinstance(event_props, dict):
                    continue
                log_group_name_value = event_props.get("LogGroupName")
                if log_group_name_value is None:
                    continue

                log_group_name = json.dumps(log_group_name_value)

                if log_group_name not in log_group_paths:
                    log_group_paths[log_group_name] = []

                log_group_paths[log_group_name].append(
                    (
                        [
                            "Resources",
                            resource_name,
                            "Properties",
                            "Events",
                            event_id,
                            "Properties",
                            "LogGroupName",
                        ],
                        # A SAM event inherits the Condition of its function
                        self.__get_condition(resource),
                    ),
                )

        return log_group_paths

    def __get_condition(self, resource: dict) -> str | None:
        """Return the resource Condition name, if it is a plain string."""
        condition = resource.get("Condition")
        if isinstance(condition, str):
            return condition
        return None

    def match(self, cfn: Template) -> RuleMatches:
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        matches.extend(self.check_events_subscription_duplicated(cfn))
        return matches
