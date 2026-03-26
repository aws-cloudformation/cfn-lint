"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.apigateway.MethodAuthorizerType import MethodAuthorizerType


@pytest.fixture(scope="module")
def rule():
    return MethodAuthorizerType()


_template = {
    "Resources": {
        "RestApi": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {"Name": "TestApi"},
        },
        "TokenAuthorizer": {
            "Type": "AWS::ApiGateway::Authorizer",
            "Properties": {
                "Name": "TokenAuth",
                "RestApiId": {"Ref": "RestApi"},
                "Type": "TOKEN",
            },
        },
        "CognitoAuthorizer": {
            "Type": "AWS::ApiGateway::Authorizer",
            "Properties": {
                "Name": "CognitoAuth",
                "RestApiId": {"Ref": "RestApi"},
                "Type": "COGNITO_USER_POOLS",
            },
        },
        "RequestAuthorizer": {
            "Type": "AWS::ApiGateway::Authorizer",
            "Properties": {
                "Name": "RequestAuth",
                "RestApiId": {"Ref": "RestApi"},
                "Type": "REQUEST",
            },
        },
        "Method": {
            "Type": "AWS::ApiGateway::Method",
            "Properties": {
                "RestApiId": {"Ref": "RestApi"},
                "ResourceId": "resource-id",
                "HttpMethod": "GET",
                "AuthorizationType": "CUSTOM",
                "AuthorizerId": {"Ref": "TokenAuthorizer"},
                "Integration": {"Type": "MOCK"},
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # CUSTOM + TOKEN — valid
        (
            _template,
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # CUSTOM + REQUEST — valid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
                            "HttpMethod": "GET",
                            "AuthorizationType": "CUSTOM",
                            "AuthorizerId": {"Ref": "RequestAuthorizer"},
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # COGNITO_USER_POOLS + COGNITO — valid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
                            "HttpMethod": "GET",
                            "AuthorizationType": "COGNITO_USER_POOLS",
                            "AuthorizerId": {"Ref": "CognitoAuthorizer"},
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # CUSTOM + COGNITO authorizer — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
                            "HttpMethod": "GET",
                            "AuthorizationType": "CUSTOM",
                            "AuthorizerId": {"Ref": "CognitoAuthorizer"},
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [
                ValidationError(
                    "'COGNITO_USER_POOLS' is not one of ['TOKEN', 'REQUEST']",
                    validator="enum",
                    rule=MethodAuthorizerType(),
                    path=deque([]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "authorizer",
                            "properties",
                            "Type",
                            "enum",
                        ]
                    ),
                    path_override=deque(
                        ["Resources", "CognitoAuthorizer", "Properties", "Type"]
                    ),
                ),
            ],
        ),
        # COGNITO_USER_POOLS + TOKEN authorizer — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
                            "HttpMethod": "GET",
                            "AuthorizationType": "COGNITO_USER_POOLS",
                            "AuthorizerId": {"Ref": "TokenAuthorizer"},
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [
                ValidationError(
                    "'COGNITO_USER_POOLS' was expected",
                    validator="const",
                    rule=MethodAuthorizerType(),
                    path=deque([]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "else",
                            "then",
                            "properties",
                            "authorizer",
                            "properties",
                            "Type",
                            "const",
                        ]
                    ),
                    path_override=deque(
                        ["Resources", "TokenAuthorizer", "Properties", "Type"]
                    ),
                ),
            ],
        ),
        # NONE — no authorizer, no error
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
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
        # AWS_IAM — no authorizer, no error
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
                            "HttpMethod": "GET",
                            "AuthorizationType": "AWS_IAM",
                            "Integration": {"Type": "MOCK"},
                        },
                    },
                },
            },
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # Hardcoded AuthorizerId string — no error
        (
            {
                "Resources": {
                    "RestApi": _template["Resources"]["RestApi"],
                    "Method": {
                        "Type": "AWS::ApiGateway::Method",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi"},
                            "ResourceId": "resource-id",
                            "HttpMethod": "GET",
                            "AuthorizationType": "CUSTOM",
                            "AuthorizerId": "abc123",
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
