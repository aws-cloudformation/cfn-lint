"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import ensure_list, is_function, load_resource
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

LOGGER = logging.getLogger(__name__)


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

        for x, y in zip(
            self.parts[5].split(delimiter), value.parts[5].split(delimiter)
        ):
            if x == y:
                continue
            if x == "*" or x.startswith("*") or y == "" or y == ".*":
                return True
            if x.startswith(y) and "*" in x:
                return True

            return False

        return True


class StatementResources(CfnLintKeyword):

    id = "I3510"
    shortdesc = "Validate statement resources match the actions"
    description = (
        "IAM policy statements have different constraints between actions and "
        "resources. This rule validates that resource ARNs or asterisks match "
        "the actions."
    )
    source_url = "https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-access-control-overview-cwl.html"
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
        for key in ["Resource", "NotResource"]:
            for resources, _ in get_value_from_path(
                validator, instance, path=deque([key])
            ):
                resources = ensure_list(resources)

                for resource in resources:
                    if not isinstance(resource, str):
                        k, v = is_function(resource)
                        if k is None:
                            continue
                        if k == "Ref" and validator.is_type(v, "string"):
                            if v in validator.context.parameters:
                                return
                        using_fn_arns = True
                        continue
                    if resource == "*":
                        return
                    all_resources.add(resource)

        all_resource_arns = [_Arn(a) for a in all_resources]
        for actions, _ in get_value_from_path(
            validator, instance, path=deque(["Action"])
        ):
            actions = ensure_list(actions)

            for action in actions:

                if not validator.is_type(action, "string"):
                    continue
                if any(x in action for x in ["*", "?"]):
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
                        # use lower as certain resources are described in actions
                        # with upper case letters and in resources as lower
                        # case issue #4036
                        arn_formats = self.service_map[service]["Resources"][
                            resource.lower()
                        ].get("ARNFormats")
                        for arn_format in arn_formats:
                            arn = _Arn(arn_format)
                        if arn in all_resource_arns:
                            break
                    else:
                        yield ValidationError(
                            (
                                f"action {action!r} requires "
                                f"a resource of {arn_formats!r}"
                            ),
                            path=deque(["Resource"]),
                            rule=self,
                        )
                else:
                    LOGGER.debug(f"action {action!r} requires a resource of '*'")
                    # yield ValidationError(
                    #    f"action {action!r} requires a resource of '*'",
                    #    path=deque(["Resource"]),
                    #    rule=self,
                    # )
