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
from cfnlint.rules.resources.apigateway.StageDeploymentRestApi import (
    StageDeploymentRestApi,
)


@pytest.fixture(scope="module")
def rule():
    return StageDeploymentRestApi()


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
        "Deployment1": {
            "Type": "AWS::ApiGateway::Deployment",
            "Properties": {"RestApiId": {"Ref": "RestApi1"}},
        },
        "Stage": {
            "Type": "AWS::ApiGateway::Stage",
            "Properties": {
                "RestApiId": {"Ref": "RestApi1"},
                "DeploymentId": {"Ref": "Deployment1"},
                "StageName": "test",
            },
        },
    },
}


def _template_with(stage_rest_api, deployment_rest_api):
    resources = copy.deepcopy(_template["Resources"])
    resources["Stage"]["Properties"]["RestApiId"] = stage_rest_api
    resources["Deployment1"]["Properties"]["RestApiId"] = deployment_rest_api
    return {"Resources": resources}


def _expected_mismatch(expected):
    return [
        ValidationError(
            f"{expected!r} was expected",
            validator="const",
            rule=StageDeploymentRestApi(),
            path=deque([]),
            schema_path=deque(
                [
                    "cfnGather",
                    "schema",
                    "cfnContext",
                    "schema",
                    "properties",
                    "deployment",
                    "properties",
                    "RestApiId",
                    "const",
                ]
            ),
            path_override=deque(
                [
                    "Resources",
                    "Deployment1",
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
            deque(["Resources", "Stage", "Properties"]),
            [],
        ),
        # Different RestApi — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Stage": {
                        "Type": "AWS::ApiGateway::Stage",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi2"},
                            "DeploymentId": {"Ref": "Deployment1"},
                            "StageName": "test",
                        },
                    },
                },
            },
            deque(["Resources", "Stage", "Properties"]),
            [
                ValidationError(
                    "{'Ref': 'RestApi2'} was expected",
                    validator="const",
                    rule=StageDeploymentRestApi(),
                    path=deque([]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "cfnContext",
                            "schema",
                            "properties",
                            "deployment",
                            "properties",
                            "RestApiId",
                            "const",
                        ]
                    ),
                    path_override=deque(
                        [
                            "Resources",
                            "Deployment1",
                            "Properties",
                            "RestApiId",
                        ]
                    ),
                ),
            ],
        ),
        # No DeploymentId — valid (no remote to check)
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Stage": {
                        "Type": "AWS::ApiGateway::Stage",
                        "Properties": {
                            "RestApiId": {"Ref": "RestApi1"},
                            "StageName": "test",
                        },
                    },
                },
            },
            deque(["Resources", "Stage", "Properties"]),
            [],
        ),
        # Ref on the Stage and GetAtt RestApiId on the Deployment name
        # the same RestApi, so there is no mismatch (#5024)
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": ["RestApi1", "RestApiId"]},
            ),
            deque(["Resources", "Stage", "Properties"]),
            [],
        ),
        # Reversed: GetAtt on the Stage and Ref on the Deployment
        (
            _template_with(
                {"Fn::GetAtt": ["RestApi1", "RestApiId"]},
                {"Ref": "RestApi1"},
            ),
            deque(["Resources", "Stage", "Properties"]),
            [],
        ),
        # GetAtt in string form is the same reference
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": "RestApi1.RestApiId"},
            ),
            deque(["Resources", "Stage", "Properties"]),
            [],
        ),
        # GetAtt on a different RestApi is still a mismatch
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": ["RestApi2", "RestApiId"]},
            ),
            deque(["Resources", "Stage", "Properties"]),
            _expected_mismatch({"Ref": "RestApi1"}),
        ),
        # GetAtt on a different attribute is not the RestApi id,
        # so it is still a mismatch
        (
            _template_with(
                {"Ref": "RestApi1"},
                {"Fn::GetAtt": ["RestApi1", "RootResourceId"]},
            ),
            deque(["Resources", "Stage", "Properties"]),
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
