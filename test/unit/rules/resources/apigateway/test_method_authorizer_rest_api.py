"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import copy
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


def _template_with(method_rest_api, authorizer_rest_api):
    resources = copy.deepcopy(_template["Resources"])
    resources["Method"]["Properties"]["RestApiId"] = method_rest_api
    resources["Authorizer1"]["Properties"]["RestApiId"] = authorizer_rest_api
    return {"Resources": resources}


def _expected_mismatch(expected):
    return [
        ValidationError(
            f"{expected!r} was expected",
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
    ]


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
        # Both sides GetAtt RestApiId name the same RestApi
        (
            _template_with(
                {"Fn::GetAtt": ["RestApi1", "RestApiId"]},
                {"Fn::GetAtt": ["RestApi1", "RestApiId"]},
            ),
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # Ref on the Method and GetAtt RestApiId on the Authorizer
        # name the same RestApi, so there is no mismatch
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": ["RestApi1", "RestApiId"]},
            ),
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # Reversed: GetAtt on the Method and Ref on the Authorizer
        (
            _template_with(
                {"Fn::GetAtt": ["RestApi1", "RestApiId"]},
                {"Ref": "RestApi1"},
            ),
            deque(["Resources", "Method", "Properties"]),
            [],
        ),
        # GetAtt on a different RestApi is still a mismatch
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": ["RestApi2", "RestApiId"]},
            ),
            deque(["Resources", "Method", "Properties"]),
            _expected_mismatch({"Ref": "RestApi1"}),
        ),
        # GetAtt on a different attribute is not the RestApi id,
        # so it is still a mismatch
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": ["RestApi1", "RootResourceId"]},
            ),
            deque(["Resources", "Method", "Properties"]),
            _expected_mismatch({"Ref": "RestApi1"}),
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
