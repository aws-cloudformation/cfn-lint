"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

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

    def __init__(self):
        """Init"""
        super().__init__(
            ["AWS::IAM::Policy/Properties/PolicyDocument/Statement/Action"]
        )
        self._service_map = load_resource(AdditionalSpecs, "Policies.json")
        self._resource_action_limitations = {
            "AWS::S3::BucketPolicy": ["s3"],
            "AWS::SQS::QueuePolicy": ["sqs"],
            "AWS::SNS::TopicPolicy": ["sns"],
        }

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        # Escape validation when using SAM transforms as a result of
        # https://github.com/aws/serverless-application-model/issues/3633
        if validator.cfn.has_serverless_transform():
            return

        actions = ensure_list(instance)

        for action in actions:
            if not validator.is_type(action, "string"):
                continue
            if action == "*":
                continue
            if ":" not in action:
                yield ValidationError(
                    (
                        f"{action!r} is not a valid action. "
                        "Must be of the form service:action or '*'"
                    ),
                    rule=self,
                )
                return
            service, permission = action.split(":", 1)
            service = service.lower()
            permission = permission.lower()

            if len(validator.context.path.cfn_path) >= 2:
                if (
                    validator.context.path.cfn_path[1]
                    in self._resource_action_limitations
                ):
                    if (
                        service
                        not in self._resource_action_limitations[
                            validator.context.path.cfn_path[1]
                        ]
                    ):
                        yield ValidationError(
                            (
                                f"{service!r} is not one of "
                                f"{self._resource_action_limitations[validator.context.path.cfn_path[1]]!r}"
                            ),
                            rule=self,
                        )

            if service in self._service_map:
                enums = list(self._service_map[service].get("Actions", []).keys())
                if permission == "*":
                    pass

                if any(x in permission for x in ["*", "?"]):
                    permission_regex = (
                        f"^{permission.replace('*', '.*').replace('?', '.')}$"
                    )
                    if not any(re.match(permission_regex, action) for action in enums):
                        yield ValidationError(
                            f"{permission!r} is not one of {enums!r}",
                            rule=self,
                        )
                elif permission not in enums:
                    yield ValidationError(
                        f"{permission!r} is not one of {enums!r}",
                        rule=self,
                    )
            else:
                yield ValidationError(
                    f"{service!r} is not one of {list(self._service_map.keys())!r}",
                    rule=self,
                )
