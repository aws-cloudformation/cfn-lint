"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class CreationPolicy(CfnLintJsonSchema):
    id = "E3055"
    shortdesc = "Check CreationPolicy values for Resources"
    description = "Check that the CreationPolicy values are valid"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-creationpolicy.html"
    tags = ["resources", "creationPolicy"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/*/CreationPolicy"],
            all_matches=True,
        )

    def _get_schema(self, resource_type: str) -> dict[str, Any]:
        if resource_type == "AWS::AppStream::Fleet":
            return {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "StartFleet": {
                        "additionalProperties": False,
                        "type": "object",
                        "properties": {"Type": {"type": "boolean"}},
                    }
                },
            }
        if resource_type == "AWS::AutoScaling::AutoScalingGroup":
            return {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "AutoScalingCreationPolicy": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "MinSuccessfulInstancesPercent": {"type": "integer"}
                        },
                    },
                    "ResourceSignal": {
                        "additionalProperties": False,
                        "type": "object",
                        "properties": {
                            "Timeout": {"type": "string"},
                            "Count": {"type": "integer"},
                        },
                    },
                },
            }
        if resource_type == "AWS::CloudFormation::WaitCondition":

            return {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "ResourceSignal": {
                        "additionalProperties": False,
                        "type": "object",
                        "properties": {
                            "Timeout": {"type": "string"},
                            "Count": {"type": "integer"},
                        },
                    }
                },
            }

        return {}

    # pylint: disable=unused-argument, arguments-renamed
    def validate(self, validator: Validator, dP: str, instance, schema):
        resource_name = validator.context.path.path[1]
        if not isinstance(resource_name, str):
            return
        resource_type = validator.context.resources[resource_name].type

        validator = validator.evolve(
            context=validator.context.evolve(
                functions=[
                    "Fn::Sub",
                    "Fn::Select",
                    "Fn::FindInMap",
                    "Fn::If",
                    "Ref",
                ],
                strict_types=False,
            ),
            schema=self._get_schema(resource_type),
        )

        yield from self._iter_errors(validator, instance)
