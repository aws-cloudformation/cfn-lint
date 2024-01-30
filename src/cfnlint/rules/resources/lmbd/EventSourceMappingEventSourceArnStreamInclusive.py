"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


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
            keywords=["aws_lambda_eventsourcemapping/eventsourcearn_stream_inclusive"]
        )
