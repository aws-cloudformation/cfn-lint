"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintRelationship import CfnLintRelationship


class InstanceImageId(CfnLintRelationship):
    id = "E3673"
    shortdesc = "Validate if an ImageId is required"
    description = (
        "Validate if an ImageID is required. It can be "
        "required if the associated LaunchTemplate doesn't specify "
        "an ImageID"
    )
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::Instance/Properties",
            ],
            relationship="Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/ImageId",
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for source_props, source_validator in self._get_relationship(
            validator, instance, path=deque(["ImageId"])
        ):
            relationships = list(self.get_relationship(source_validator))
            if not relationships and not source_props:
                yield ValidationError(
                    "'ImageId' is a required property",
                    path_override=(
                        source_validator.context.path.path
                        if len(source_validator.context.path.path) > 4
                        else deque([])
                    ),
                )
            for relationship_props, _ in relationships:
                if relationship_props is None:
                    if not source_props:
                        yield ValidationError(
                            "'ImageId' is a required property",
                            path_override=(
                                source_validator.context.path.path
                                if len(source_validator.context.path.path) > 4
                                else deque([])
                            ),
                        )
