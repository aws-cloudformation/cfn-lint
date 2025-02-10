"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.extensions.aws_sqs_queue
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class QueueProperties(CfnLintJsonSchema):
    id = "E3501"
    shortdesc = "Validate SQS queue properties are valid"
    description = (
        "Depending on if the queue is FIFO or not the "
        "properties and allowed values change. "
        "This rule validates properties and values based on the queue type."
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
                filename="properties.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            if err.schema is False:
                err.message = (
                    f"Additional properties are not allowed ({err.path[-1]!r} "
                    "was unexpected)"
                )

            yield err
