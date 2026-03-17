"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

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
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"
