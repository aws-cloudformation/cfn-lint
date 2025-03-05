"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.apigateway.RestApiMixingDefinitions import (
    RestApiMixingDefinitions,
)


@pytest.fixture(scope="module")
def rule():
    rule = RestApiMixingDefinitions()
    yield rule


@pytest.fixture
def path():
    return Path(
        path=deque(["Resources", "RestApi", "Properties", "Body"]),
        cfn_path=deque(["Resources", "AWS::ApiGateway::RestApi", "Properties", "Body"]),
    )


_rest_api = {
    "Type": "AWS::ApiGateway::RestApi",
    "Properties": {},
}

_api_resource = {
    "Type": "AWS::ApiGateway::Resource",
    "Properties": {
        "RestApiId": {"Ref": "RestApi"},
        "ParentId": {"Fn::GetAtt": "RestApi.RootResourceId"},
        "PathPart": "test",
    },
}

_api_model = {
    "Type": "AWS::ApiGateway::Model",
    "Properties": {
        "RestApiId": {"Ref": "RestApi"},
        "ContentType": "application/json",
        "Description": "Schema for Pets example",
        "Name": "PetsModelNoFlatten",
        "Schema": {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "PetsModelNoFlatten",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer"},
                    "class": {"type": "string"},
                    "salesPrice": {"type": "number"},
                },
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,expected",
    [
        (
            {
                "Resources": {
                    "RestApi": _rest_api,
                }
            },
            [],
        ),
        (
            {
                "Resources": {
                    "RestApi": _rest_api,
                    "RootResource": _api_resource,
                }
            },
            [
                ValidationError(
                    (
                        "Defining 'Body' with a relation to "
                        "resource 'RootResource' of type "
                        "'AWS::ApiGateway::Resource' may result "
                        "in drift and orphaned resources"
                    ),
                    rule=RestApiMixingDefinitions(),
                    path=deque([]),
                )
            ],
        ),
        (
            {
                "Resources": {
                    "RestApi": _rest_api,
                    "RootResource": _api_resource,
                    "Model": _api_model,
                }
            },
            [
                ValidationError(
                    (
                        "Defining 'Body' with a relation to "
                        "resource 'RootResource' of type "
                        "'AWS::ApiGateway::Resource' may result "
                        "in drift and orphaned resources"
                    ),
                    rule=RestApiMixingDefinitions(),
                ),
                ValidationError(
                    (
                        "Defining 'Body' with a relation to "
                        "resource 'Model' of type "
                        "'AWS::ApiGateway::Model' may result "
                        "in drift and orphaned resources"
                    ),
                    rule=RestApiMixingDefinitions(),
                ),
            ],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, expected, rule, validator):
    errs = list(rule.validate(validator, "", "", {}))

    assert errs == expected, f"Expected {expected} got {errs}"
