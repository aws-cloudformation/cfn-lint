"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class EventSourceMappingEventSourceArnSqsExclusive(BaseCfnSchema):
    id = "E3634"
    shortdesc = (
        "Validate Lambda event source mapping starting position is used with SQS"
    )
    description = (
        "When 'EventSourceArn' is associated to SQS don't specify 'StartingPosition'"
    )
    tags = ["resources"]
    schema_path = "aws_lambda_eventsourcemapping/eventsourcearn_sqs_exclusive"
