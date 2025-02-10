"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

import cfnlint.data.schemas.extensions.aws_sqs_queue
from cfnlint.helpers import bool_compare, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class QueueDLQ(CfnLintJsonSchema):
    id = "E3502"
    shortdesc = "Validate SQS DLQ queues are the same type"
    description = (
        "SQS queues using DLQ have to have the destination "
        "queue as the same type (FIFO or standard)"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sqs-queue.html"
    tags = ["resources", "sqs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::SQS::Queue/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sqs_queue,
                filename="properties.json",
            ),
            all_matches=True,
        )

    def _is_fifo_queue(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[str, Validator]]:
        standard = "standard"
        fifo = "FIFO"

        if "FifoQueue" not in instance:
            yield standard, validator
            return

        for queue_type, queue_type_validator in get_value_from_path(
            validator=validator, instance=instance, path=deque(["FifoQueue"])
        ):
            yield (
                fifo if bool_compare(queue_type, True) else standard
            ), queue_type_validator

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for queue_type, queue_type_validator in self._is_fifo_queue(
            validator=validator,
            instance=instance,
        ):
            queue_type_validator = queue_type_validator.evolve(
                context=queue_type_validator.context.evolve(
                    path=validator.context.path.evolve()
                )
            )

            for target, target_validator in get_value_from_path(
                queue_type_validator,
                instance,
                path=deque(["RedrivePolicy", "deadLetterTargetArn"]),
            ):
                k, v = is_function(target)
                if k != "Fn::GetAtt":
                    return

                if target_validator.is_type(v, "string"):
                    v = v.split(".")

                if len(v) < 1:
                    return

                dest_queue = validator.cfn.template.get("Resources", {}).get(v[0], {})

                if dest_queue.get("Type") != "AWS::SQS::Queue":
                    return

                for dest_queue_type, _ in self._is_fifo_queue(
                    target_validator,
                    instance=dest_queue.get("Properties", {}),
                ):
                    if queue_type != dest_queue_type:
                        yield ValidationError(
                            (
                                f"Source queue type {queue_type!r} does not "
                                f"match destination queue type {dest_queue_type!r}"
                            ),
                            rule=self,
                            path=target_validator.context.path.path,
                        )
