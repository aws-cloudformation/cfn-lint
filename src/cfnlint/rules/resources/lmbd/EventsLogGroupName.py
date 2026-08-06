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
        "Check for SubscriptionFilters have beyond 2 attachments to a CloudWatch Log"
        " Group"
    )
    description = (
        "The current limit for a CloudWatch Log Group is they can have 2 subscription"
        " filters. We will look for duplicate LogGroupNames inside Subscription Filters"
        " and make sure they are within 2. This doesn't account for any other"
        " subscription filters getting set."
    )
    source_url = "https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#user-content-cloudwatchlogs"
    tags = ["resources", "lambda"]
    limit = 2

    def check_events_subscription_duplicated(self, cfn: Template) -> RuleMatches:
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        message = (
            f"You can only have {self.limit} Subscription Filters per CloudWatch Log"
            " Group"
        )

        log_group_paths = self.__get_log_group_name_list(cfn)
        for _, paths in log_group_paths.items():
            if len(paths) > self.limit:
                matches.append(RuleMatch(paths[2], message))

        return matches

    def __get_log_group_name_list(
        self,
        cfn: Template,
    ) -> dict[str, list[list[str | int]]]:
        log_group_paths: dict[str, list[list[str | int]]] = {}

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
                ["Resources", resource_name, "Properties", "LogGroupName"],
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
                    [
                        "Resources",
                        resource_name,
                        "Properties",
                        "Events",
                        event_id,
                        "Properties",
                        "LogGroupName",
                    ],
                )

        return log_group_paths

    def match(self, cfn: Template) -> RuleMatches:
        """Check if Lambda Events Subscription is duplicated"""
        matches = []
        matches.extend(self.check_events_subscription_duplicated(cfn))
        return matches
