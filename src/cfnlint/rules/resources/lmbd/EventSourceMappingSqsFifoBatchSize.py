"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EventSourceMappingSqsFifoBatchSize(CfnLintJsonSchema):
    id = "E3705"
    shortdesc = "Validate SQS FIFO queue EventSourceMapping BatchSize is at most 10"
    description = (
        "When an EventSourceMapping references a FIFO SQS queue, "
        "the BatchSize must be at most 10"
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
                filename="event_source_sqs_fifo_batch_size.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
