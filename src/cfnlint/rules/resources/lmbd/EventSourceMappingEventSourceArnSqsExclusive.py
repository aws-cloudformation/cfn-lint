"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EventSourceMappingEventSourceArnSqsExclusive(CfnLintJsonSchema):
    id = "E3634"
    shortdesc = (
        "Validate Lambda event source mapping starting position is used with SQS"
    )
    description = (
        "When 'EventSourceArn' is associated to SQS don't specify 'StartingPosition'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::EventSourceMapping/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping,
                filename="eventsourcearn_sqs_exclusive.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "Additional properties are not allowed ('StartingPosition')"
