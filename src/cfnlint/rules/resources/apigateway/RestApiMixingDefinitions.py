"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class RestApiMixingDefinitions(CfnLintKeyword):
    id = "W3660"
    shortdesc = "Validate if multiple resources are modifying a Rest API definition"
    description = (
        "When using AWS::ApiGateway::RestApi with 'Body' or 'BodyS3Location' "
        "the resource handler will use PutRestApi with mode overwrite. "
        "Depending on how resources are updated the IaC template will "
        "drift and create orphaned resources."
    )
    tags = ["resources", "apigateway"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ApiGateway::RestApi/Properties/Body",
                "Resources/AWS::ApiGateway::RestApi/Properties/BodyS3Location",
            ],
        )
        self._mix_types = [
            "AWS::ApiGateway::Method",
            "AWS::ApiGateway::Model",
            "AWS::ApiGateway::Resource",
            "AWS::ApiGateway::GatewayResponse",
            "AWS::ApiGateway::RequestValidator",
            "AWS::ApiGateway::Authorizer",
        ]

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if validator.cfn.graph is None:  # pragma: no cover
            return  # pragma: no cover

        if not len(validator.context.path.path) > 3:
            return

        resource_name = validator.context.path.path[1]
        key = validator.context.path.path[3]

        unique_sources: set[str] = set()
        for source, _ in validator.cfn.graph.graph.in_edges(resource_name):
            if source not in validator.context.resources:
                continue
            if validator.context.resources[source].type in self._mix_types:
                if source not in unique_sources:
                    yield ValidationError(
                        message=(
                            f"Defining {key!r} with a relation to resource {source!r} "
                            f"of type {validator.context.resources[source].type!r} "
                            "may result in drift and orphaned resources"
                        ),
                        rule=self,
                    )
                    unique_sources.add(source)
