"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema



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
        super().__init__(keywords=["aws_lambda_eventsourcemapping/eventsourcearn_sqs_exclusive"])

