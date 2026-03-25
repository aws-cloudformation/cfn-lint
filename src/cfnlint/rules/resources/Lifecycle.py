"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class ResourceLifecycle(CloudFormationLintRule):
    id = "E3710"
    shortdesc = "Resource type is from a service that has been shut down"
    description = (
        "Checks if a resource type belongs to an AWS service that has "
        "reached full shutdown and is no longer available"
    )
    source_url = (
        "https://docs.aws.amazon.com/general/latest/gr/full_shutdown_services.html"
    )
    tags = ["resources", "lifecycle"]

    def __init__(self) -> None:
        super().__init__()
        self.child_rules = {
            "W3696": None,
            "W3697": None,
        }

    _messages = {
        "shutdown": (
            "Resource type {type_name!r} is from a service that has been shut down"
        ),
        "sunset": ("Resource type {type_name!r} is from a service that is sunsetting"),
        "maintenance": (
            "Resource type {type_name!r} is from a service in maintenance mode"
        ),
    }

    _messages_with_date = {
        "shutdown": (
            "Resource type {type_name!r} is from a service that was shut down on {date}"
        ),
        "sunset": (
            "Resource type {type_name!r} is from a service that will "
            "be shut down on {date}. Plan to migrate to an alternative"
        ),
        "maintenance": (
            "Resource type {type_name!r} is from a service in maintenance "
            "mode since {date}. Consider migrating to an alternative"
        ),
    }

    def lifecycle(self, validator: Validator, lc: Any, instance: Any, schema: Any):
        if not isinstance(lc, dict):
            return

        status = lc.get("status", "")
        date = lc.get("date")
        type_name = schema.get("typeName", "")

        if date:
            msg = self._messages_with_date.get(status, "")
            msg = msg.format(type_name=type_name, date=date)
        else:
            msg = self._messages.get(status, "")
            msg = msg.format(type_name=type_name)
        if not msg:
            return

        if status == "shutdown":
            yield ValidationError(msg, rule=self)
        elif status == "sunset":
            rule = self.child_rules.get("W3696")
            if rule:
                yield ValidationError(msg, rule=rule)
        elif status == "maintenance":
            rule = self.child_rules.get("W3697")
            if rule:
                yield ValidationError(msg, rule=rule)
