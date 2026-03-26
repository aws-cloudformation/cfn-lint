"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.apigateway.MethodAuthorizerRestApi import (
    MethodAuthorizerRestApi,
)


@pytest.fixture(scope="module")
def rule():
    return MethodAuthorizerRestApi()


_template = {
    "Resources": {
        "RestApi1": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {"Name": "Api1"},
        },
        "RestApi2": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {"Name": "Api2"},
        },
        "Authorizer1": {
            "Type": "AWS::ApiGateway::Authorizer",
            "Properties": {
                "Name": "Auth",
                "RestApiId": {"Ref": "RestApi1"},
                "Type": "TOKEN",
            },
        },
        "Method": {
            "Type": "AWS::ApiGateway::Method",
            "Properties": {
                "RestApiId": {"Ref": "RestApi1"},
                "ResourceId": "rid",
                "HttpMethod": "GET",
                "AuthorizationType": "CUSTOM",
                "AuthorizerId": {"Ref": "Authorizer1"},
                "Integration": {"Type": "MOCK"},
            },
        },
    },
}

_schema_path = deque(
    [
        "cfnGather",
        "schema",
        "cfnContext",
        "schema",
        "properties",
        "authorizer",
        "properties",
        "RestApiId",
        "const",
    ]
)


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # Same RestApi — valid
        (
            _template,
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # Different RestApi — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi2"},
                            "ResourceId": "rid",
                            "HttpMethod": "GET",
                            "AuthorizationType": "CUSTOM",
                            "AuthorizerId": {"Ref": "Authorizer1"},
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [
                ValidationError(
                    "{'Ref': 'RestApi2'} was expected",
                    validator="const",
                    rule=MethodAuthorizerRestApi(),
                    path=deque([]),
                    schema_path=_schema_path,
                    path_override=deque(
                        [
                            "Resources",
                            "Authorizer1",
                            "Properties",
                            "RestApiId",
                        ]
                    ),
                ),
            ],
        ),
        # No AuthorizerId — valid (no remote to check)
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi1"},
                            "ResourceId": "rid",
                            "HttpMethod": "GET",
                            "AuthorizationType": "NONE",
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"
