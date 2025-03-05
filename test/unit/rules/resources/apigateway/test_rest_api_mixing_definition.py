"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.apigateway.RestApiMixingDefinitions import (
    RestApiMixingDefinitions,
)


@pytest.fixture(scope="module")
def rule():
    rule = RestApiMixingDefinitions()
    yield rule


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

_api_stage = {
    "Type": "AWS::ApiGateway::Stage",
    "Properties": {
        "StageName": "Prod",
        "Description": "Prod Stage",
        "RestApiId": {"Ref": "RestApi"},
    },
}


@pytest.mark.parametrize(
    "template,path,expected",
    [
        (
            {
                "Resources": {
                    "RestApi": _rest_api,
                }
            },
            {
                "path": deque(["Resources", "RestApi", "Properties", "Body"]),
            },
            [],
        ),
        (
            {
                "Resources": {
                    "RestApi": _rest_api,
                    "ProdStage": _api_stage,
                },
                "Outputs": {"RestApiId": {"Value": {"Ref": "RestApi"}}},
            },
            {
                "path": deque(["Resources", "RestApi", "Properties", "Body"]),
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
            {
                "path": deque(["Resources", "RestApi", "Properties", "Body"]),
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
                }
            },
            {
                "path": deque(["Resources", "RestApi"]),
            },
            [],
        ),
        (
            {
                "Resources": {
                    "RestApi": _rest_api,
                    "RootResource": _api_resource,
                    "Model": _api_model,
                }
            },
            {
                "path": deque(["Resources", "RestApi", "Properties", "Body"]),
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
    indirect=["template", "path"],
)
def test_validate(template, path, expected, rule, validator):
    errs = list(rule.validate(validator, "", "", {}))

    assert errs == expected, f"Expected {expected} got {errs}"
