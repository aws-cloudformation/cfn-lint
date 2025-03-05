"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class EventSourceMappingToSqsTimeout(CfnLintKeyword):

    id = "E3505"
    shortdesc = (
        "Validate SQS 'VisibilityTimeout' is greater than a function's 'Timeout'"
    )
    description = (
        "When attaching a Lambda function to a SQS queue to a Lambda function the "
        "SQS 'VisibilityTimeout' has to be greater than or equal to "
        " the lambda functions's 'Timeout'"
    )
    source_url = "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html"
    tags = ["resources", "lambda", "sqs"]

    def __init__(self):
        """Init"""
        super().__init__(["Resources/AWS::Lambda::Function/Properties/Timeout"])

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if validator.is_type(instance, "string"):
            try:
                instance = int(instance)
            except:  # noqa: E722
                return

        if not validator.is_type(instance, "integer"):
            return

        if validator.cfn.graph is None:  # pragma: no cover
            return  # pragma: no cover

        if not len(validator.context.path.path) >= 2:
            return

        resource_name = validator.context.path.path[1]
        for child_1, _ in validator.cfn.graph.graph.in_edges(resource_name):
            if child_1 not in validator.context.resources:
                continue

            if (
                validator.context.resources[child_1].type
                == "AWS::Lambda::EventSourceMapping"
            ):
                for _, child_2 in validator.cfn.graph.graph.out_edges(child_1):
                    if child_2 not in validator.context.resources:
                        continue
                    if validator.context.resources[child_2].type == "AWS::SQS::Queue":
                        for visibility_timeout, _ in get_value_from_path(
                            validator,
                            validator.cfn.template,
                            deque(
                                [
                                    "Resources",
                                    child_2,
                                    "Properties",
                                    "VisibilityTimeout",
                                ]
                            ),
                        ):
                            if validator.is_type(visibility_timeout, "string"):
                                try:
                                    visibility_timeout = int(visibility_timeout)
                                except:  # noqa: E722
                                    continue

                            if not validator.is_type(visibility_timeout, "integer"):
                                continue

                            if visibility_timeout < instance:
                                yield ValidationError(
                                    message=(
                                        f"Queue visibility timeout "
                                        f"({visibility_timeout!r}) "
                                        "is less than Function timeout "
                                        f"({instance!r}) seconds"
                                    ),
                                    rule=self,
                                )
