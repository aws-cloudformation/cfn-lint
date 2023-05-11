"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class EventSourceMappingEventSourceArnStreamInclusive(BaseCfnSchema):
    id = "E3633"
    shortdesc = "Validate Lambda event source mapping StartingPosition is used correctly"
    description = "When 'EventSourceArn' is associate to Kinesis, Kafka, or DynamoDB you must specify 'StartingPosition"
    tags = ["resources"]
    schema_path = "aws_lambda_eventsourcemapping/eventsourcearn_stream_inclusive"
