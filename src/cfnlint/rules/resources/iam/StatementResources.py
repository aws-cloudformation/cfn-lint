"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import ensure_list, load_resource
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class _Arn:

    def __init__(self, full_arn: str):
        arn_parts = full_arn.split(":", 5)

        self._parts: list[str] = ["*", "*", "*", "*", "*", "*"]

        for i, arn_part in enumerate(arn_parts):
            self._parts[i] = arn_part

    def __repr__(self):
        return ":".join(self._parts)

    @property
    def parts(self):
        return self._parts

    def __eq__(self, value: Any):
        if not isinstance(value, _Arn):
            return False

        if len(value.parts) != len(self._parts):
            return False

        for i in range(0, 5):
            if self.parts[i] == "*":
                continue
            if value.parts[i] in ["${Partition}", "${Region}", "${Account}"]:
                continue
            if self.parts[i] != value.parts[i]:
                return False

        if self.parts[5] == "*":
            return True

        delimiter = None
        if ":" in value.parts[5]:
            delimiter = ":"
        elif "/" in value.parts[5]:
            delimiter = "/"

        if not delimiter:
            return True

        value_resource_parts = value.parts[5].split(delimiter)
        for i, resource_part in enumerate(self.parts[5].split(delimiter)):
            if resource_part == "*":
                return True
            if i > len(value_resource_parts):
                return True
            if value_resource_parts[i] == ".*":
                return True
            if (
                resource_part.startswith(value_resource_parts[i])
                and "*" in resource_part
            ):
                return True
            if resource_part != value_resource_parts[i]:
                return False

        return True


class StatementResources(CfnLintKeyword):

    id = "I3510"
    shortdesc = "Validate statement resources match the actions"
    description = (
        "IAM policy statements have different constraints between actions and "
        "resources. This rule validates that actions that require an "
        "asterisk resource have an asterisk resource."
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html"
    tags = ["resources", "iam"]

    def __init__(self):
        super().__init__(
            ["AWS::IAM::Policy/Properties/PolicyDocument/Statement"],
        )
        self.service_map = load_resource(AdditionalSpecs, "Policies.json")

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if not validator.is_type(instance, "object"):
            return

        using_fn_arns = False
        all_resources: set[str] = set()
        for resources, _ in get_value_from_path(
            validator, instance, path=deque(["Resource"])
        ):
            resources = ensure_list(resources)

            for resource in resources:
                if not isinstance(resource, str):
                    using_fn_arns = True
                    continue
                all_resources.add(resource)

        if "*" in all_resources:
            return

        all_resource_arns = [_Arn(a) for a in all_resources]
        for actions, _ in get_value_from_path(
            validator, instance, path=deque(["Action"])
        ):
            actions = ensure_list(actions)

            for action in actions:

                if "*" in action:
                    continue
                if ":" not in action:
                    continue
                service, permission = action.split(":", 1)
                service = service.lower()
                permission = permission.lower()

                if service not in self.service_map:
                    continue

                if permission not in self.service_map[service]["Actions"]:
                    continue

                resources = self.service_map[service]["Actions"][permission].get(
                    "Resources", None
                )
                if isinstance(resources, (list, str)):
                    if using_fn_arns:
                        continue
                    resources = ensure_list(resources)
                    for resource in resources:
                        arn_formats = self.service_map[service]["Resources"][
                            resource
                        ].get("ARNFormats")
                        for arn_format in arn_formats:
                            arn = _Arn(arn_format)
                            if arn not in all_resource_arns:
                                yield ValidationError(
                                    (
                                        f"action {action!r} requires "
                                        f"a resource of {arn_formats!r}"
                                    ),
                                    path=deque(["Resource"]),
                                    rule=self,
                                )
                else:
                    yield ValidationError(
                        f"action {action!r} requires a resource of '*'",
                        path=deque(["Resource"]),
                        rule=self,
                    )
