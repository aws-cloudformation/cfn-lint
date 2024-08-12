"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import ensure_list, load_resource
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class Permissions(CfnLintKeyword):
    """Check IAM Permission configuration"""

    id = "W3037"
    shortdesc = "Check IAM Permission configuration"
    description = "Check for valid IAM Permissions"
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_action.html"
    tags = ["properties", "iam", "permissions"]
    experimental = True

    def __init__(self):
        """Init"""
        super().__init__(
            ["AWS::IAM::Policy/Properties/PolicyDocument/Statement/Action"]
        )
        self.service_map = self.load_service_map()

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        actions = ensure_list(instance)

        for action in actions:
            if action == "*":
                continue
            if ":" not in action:
                yield ValidationError(
                    (
                        f"{action!r} is not a valid action."
                        "Must be of the form service:action or '*'"
                    ),
                    rule=self,
                )
                return
            service, permission = action.split(":", 1)
            service = service.lower()
            permission = permission.lower()

            if service in self.service_map:
                enums = self.service_map[service]
                if permission == "*":
                    pass
                elif permission.endswith("*"):
                    wilcarded_permission = permission.split("*")[0]
                    if not any(wilcarded_permission in action for action in enums):
                        yield ValidationError(
                            f"{permission!r} is not one of {enums!r}",
                            rule=self,
                        )

                elif permission.startswith("*"):
                    wilcarded_permission = permission.split("*")[1]
                    if not any(
                        wilcarded_permission in action
                        for action in self.service_map[service]
                    ):
                        yield ValidationError(
                            f"{permission!r} is not one of {enums!r}",
                            rule=self,
                        )
                elif permission not in self.service_map[service]:
                    yield ValidationError(
                        f"{permission!r} is not one of {enums!r}",
                        rule=self,
                    )
            else:
                yield ValidationError(
                    f"{service!r} is not one of {list(self.service_map.keys())!r}",
                    rule=self,
                )

    def load_service_map(self):
        """
        Convert policies.json into a simpler version for more efficient key lookup.
        """
        service_map = load_resource(AdditionalSpecs, "Policies.json")["serviceMap"]

        policy_service_map = {}

        for _, properties in service_map.items():
            # The services and actions are case insensitive
            service = properties["StringPrefix"].lower()
            actions = [x.lower() for x in properties["Actions"]]

            # Some services have the same name for different
            # generations; like elasticloadbalancing.
            if service in policy_service_map:
                policy_service_map[service] += actions
            else:
                policy_service_map[service] = actions

        return policy_service_map
