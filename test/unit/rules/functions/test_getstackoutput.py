"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.GetStackOutput import GetStackOutput


@pytest.fixture(scope="module")
def rule():
    rule = GetStackOutput()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid with required fields only",
            {
                "Fn::GetStackOutput": {
                    "StackName": "producer-stack",
                    "OutputName": "MyOutput",
                }
            },
            {"type": "string"},
            [],
        ),
        (
            "Valid with all fields",
            {
                "Fn::GetStackOutput": {
                    "StackName": "producer-stack",
                    "OutputName": "MyOutput",
                    "Region": "us-east-1",
                    "RoleArn": "arn:aws:iam::123456789012:role/role",
                }
            },
            {"type": "string"},
            [],
        ),
        (
            "Valid with Ref inside StackName",
            {
                "Fn::GetStackOutput": {
                    "StackName": {"Ref": "StackNameParam"},
                    "OutputName": "MyOutput",
                }
            },
            {"type": "string"},
            [],
        ),
        (
            "Invalid - missing OutputName",
            {
                "Fn::GetStackOutput": {
                    "StackName": "producer-stack",
                }
            },
            {"type": "string"},
            [
                ValidationError(
                    "'OutputName' is a required property",
                    path=deque(["Fn::GetStackOutput"]),
                    schema_path=deque(["cfnContext", "schema", "required"]),
                    validator="fn_getstackoutput",
                )
            ],
        ),
        (
            "Invalid - missing StackName",
            {
                "Fn::GetStackOutput": {
                    "OutputName": "MyOutput",
                }
            },
            {"type": "string"},
            [
                ValidationError(
                    "'StackName' is a required property",
                    path=deque(["Fn::GetStackOutput"]),
                    schema_path=deque(["cfnContext", "schema", "required"]),
                    validator="fn_getstackoutput",
                )
            ],
        ),
        (
            "Invalid - wrong value type (string instead of object)",
            {"Fn::GetStackOutput": "just-a-string"},
            {"type": "string"},
            [
                ValidationError(
                    "'just-a-string' is not of type 'object'",
                    path=deque(["Fn::GetStackOutput"]),
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    validator="fn_getstackoutput",
                )
            ],
        ),
        (
            "Invalid - wrong output type (expects array but returns string)",
            {
                "Fn::GetStackOutput": {
                    "StackName": "producer-stack",
                    "OutputName": "MyOutput",
                }
            },
            {"type": "array"},
            [
                ValidationError(
                    (
                        "{'Fn::GetStackOutput': {'StackName': 'producer-stack',"
                        " 'OutputName': 'MyOutput'}} is not of type 'array'"
                    ),
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_getstackoutput",
                ),
            ],
        ),
        (
            "Invalid - additional property",
            {
                "Fn::GetStackOutput": {
                    "StackName": "producer-stack",
                    "OutputName": "MyOutput",
                    "InvalidKey": "value",
                }
            },
            {"type": "string"},
            [
                ValidationError(
                    (
                        "Additional properties are not allowed"
                        " ('InvalidKey' was unexpected)"
                    ),
                    path=deque(["Fn::GetStackOutput", "InvalidKey"]),
                    schema_path=deque(["cfnContext", "schema", "additionalProperties"]),
                    validator="fn_getstackoutput",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_getstackoutput(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
