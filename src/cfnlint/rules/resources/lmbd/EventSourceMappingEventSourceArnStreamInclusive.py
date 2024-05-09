"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class EventSourceMappingEventSourceArnStreamInclusive(CfnLintJsonSchema):
    id = "E3633"
    shortdesc = (
        "Validate Lambda event source mapping StartingPosition is used correctly"
    )
    description = (
        "When 'EventSourceArn' is associate to Kinesis, Kafka, "
        "or DynamoDB you must specify 'StartingPosition"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::EventSourceMapping/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_eventsourcemapping,
                filename="eventsourcearn_stream_inclusive.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "'StartingPosition' is a required property"
