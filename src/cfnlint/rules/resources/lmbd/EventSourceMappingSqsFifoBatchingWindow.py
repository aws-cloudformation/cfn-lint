"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EventSourceMappingSqsFifoBatchingWindow(CfnLintJsonSchema):
    id = "E3729"
    shortdesc = "Validate SQS FIFO queue EventSourceMapping has no batching window"
    description = (
        "When an EventSourceMapping references a FIFO SQS queue, "
        "MaximumBatchingWindowInSeconds must be omitted or 0. Lambda rejects "
        "the mapping with 'Batching window is not supported for FIFO queues'."
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html"
    tags = ["resources", "lambda", "sqs"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Lambda::EventSourceMapping/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping,
                filename="event_source_sqs_fifo_batching_window.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{err.message} when the event source is an SQS FIFO queue"
