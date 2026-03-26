"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EventSourceMappingToSqsTimeout(CfnLintJsonSchema):
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

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Lambda::EventSourceMapping/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping,
                filename="event_source_sqs_timeout.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            f"Queue visibility timeout ({err.instance!r}) is less "
            f"than Function timeout ({err.schema.get('minimum')!r}) seconds"
        )

    def _clean_error(self, err: ValidationError) -> ValidationError:
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
