"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule


class Permissions(CloudFormationLintRule):
    """Check IAM Permission configuration"""

    id = "W3037"
    shortdesc = "Check IAM Permission configuration"
    description = "Check for valid IAM Permissions"
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_action.html"
    tags = ["properties", "iam", "permissions"]
    experimental = True

    def __init__(self):
        """Init"""
        super().__init__()
        self.service_map = self.load_service_map()

    def iampolicystatementaction(self, validator, _, instance, schema):
        actions = ensure_list(instance)

        for action in actions:
            if action == "*":
                continue
            service, permission = action.split(":", 1)
            service = service.lower()
            permission = permission.lower()

            if service in self.service_map:
                enums = self.service_map[service]
                if permission == "*":
                    pass
                elif service.endswith("*"):
                    wilcarded_permission = permission.split("*")[0]
                    if not any(wilcarded_permission in action for action in enums):
                        yield ValidationError(f"{permission!r} is not one of {enums!r}")

                elif permission.startswith("*"):
                    wilcarded_permission = permission.split("*")[1]
                    if not any(
                        wilcarded_permission in action
                        for action in self.service_map[service]
                    ):
                        yield ValidationError(f"{permission!r} is not one of {enums!r}")
                elif permission not in self.service_map[service]:
                    yield ValidationError(f"{permission!r} is not one of {enums!r}")
            else:
                yield ValidationError(
                    f"{service!r} is not one of {list(self.service_map.keys)!r}"
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
