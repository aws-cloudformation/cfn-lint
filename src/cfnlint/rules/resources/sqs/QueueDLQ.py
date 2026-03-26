"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_sqs_queue
from cfnlint.helpers import bool_compare
from cfnlint.jsonschema import ValidationError
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
                filename="queue_dlq.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        # Extract the gathered object from the error path
        # The error is on the gathered object, not the original instance
        # Check the expected value from the schema to determine the message
        if err.validator == "const" and "const" in err.schema:
            expected = err.schema["const"]
            # Normalize to boolean for comparison
            if bool_compare(expected, True):
                return (
                    "Source queue type 'standard' does not "
                    "match destination queue type 'FIFO'"
                )
            elif bool_compare(expected, False):
                return (
                    "Source queue type 'FIFO' does not match "
                    "destination queue type 'standard'"
                )
        return self.shortdesc

    def _iter_errors(self, validator, instance):
        """Override to apply custom messages to all errors"""
        errs = list(validator.iter_errors(instance))
        for err in errs:
            err = self._clean_error(err)
            err.message = self.message(instance, err)
            yield err
