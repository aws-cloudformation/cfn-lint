"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.CreationPolicy import CreationPolicy


@pytest.fixture
def rule():
    return CreationPolicy()


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyInstance": {
                "Type": "AWS::EC2::Instance",
            },
            "MyWaitCondition": {
                "Type": "AWS::CloudFormation::WaitCondition",
            },
            "MyAutoScalingGroup": {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
            },
            "MyAppStreamFleet": {
                "Type": "AWS::AppStream::Fleet",
            },
            "MyLambdaFunction": {
                "Type": "AWS::Lambda::Function",
            },
        }
    }


@pytest.mark.parametrize(
    "name, instance, path, expected",
    [
        (
            "Correct for app stream",
            {"StartFleet": {"Type": True}},
            {
                "path": deque(["Resources", "MyAppStreamFleet", "CreationPolicy"]),
            },
            [],
        ),
        (
            "Bad type for app stream",
            {
                "StartFleet": {
                    "Type": {},
                }
            },
            {
                "path": deque(["Resources", "MyAppStreamFleet", "CreationPolicy"]),
            },
            [
                ValidationError(
                    "{} is not of type 'boolean'",
                    rule=CreationPolicy(),
                    path=deque(["StartFleet", "Type"]),
                    schema_path=deque(
                        ["properties", "StartFleet", "properties", "Type", "type"]
                    ),
                    validator="type",
                )
            ],
        ),
        (
            "Valid ASG",
            {
                "AutoScalingCreationPolicy": {"MinSuccessfulInstancesPercent": 100},
                "ResourceSignal": {"Count": 1, "Timeout": "60"},
            },
            {
                "path": deque(["Resources", "MyAutoScalingGroup", "CreationPolicy"]),
            },
            [],
        ),
        (
            "Invalid ASG",
            {
                "AutoScalingCreationPolicy": {"MinSuccessfulInstancesPercent": 100},
                "ResourceSignal": {"Count": "one", "Timeout": "60"},
            },
            {
                "path": deque(["Resources", "MyAutoScalingGroup", "CreationPolicy"]),
            },
            [
                ValidationError(
                    "'one' is not of type 'integer'",
                    rule=CreationPolicy(),
                    path=deque(["ResourceSignal", "Count"]),
                    schema_path=deque(
                        ["properties", "ResourceSignal", "properties", "Count", "type"]
                    ),
                    validator="type",
                )
            ],
        ),
        (
            "Valid Wait Condition",
            {"ResourceSignal": {"Timeout": "PT15M", "Count": "5"}},
            {
                "path": deque(["Resources", "MyWaitCondition", "CreationPolicy"]),
            },
            [],
        ),
        (
            "Invalid Wait Condition",
            {"ResourceSignal": {"Timeout": "PT15M", "Count": "five"}},
            {
                "path": deque(["Resources", "MyWaitCondition", "CreationPolicy"]),
            },
            [
                ValidationError(
                    "'five' is not of type 'integer'",
                    rule=CreationPolicy(),
                    path=deque(["ResourceSignal", "Count"]),
                    schema_path=deque(
                        ["properties", "ResourceSignal", "properties", "Count", "type"]
                    ),
                    validator="type",
                )
            ],
        ),
        (
            "Valid instance",
            {"ResourceSignal": {"Timeout": "PT15M", "Count": "5"}},
            {
                "path": deque(["Resources", "MyWaitCondition", "CreationPolicy"]),
            },
            [],
        ),
        (
            "Invalid Instance",
            {"Foo": {"Bar"}},
            {
                "path": deque(["Resources", "MyInstance", "CreationPolicy"]),
            },
            [],
        ),
        (
            "Wait condition ignored on wrong type",
            {"Foo": {"Bar"}},
            {
                "path": deque(["Resources", "MyLambdaFunction", "CreationPolicy"]),
            },
            [],
        ),
        (
            "Invalid but integer name ",
            {"ResourceSignal": {"Timeout": "PT15M", "Count": "five"}},
            {
                "path": deque(["Resources", 1, "CreationPolicy"]),
            },
            [],
        ),
    ],
    indirect=["path"],
)
def test_deletion_policy(name, instance, expected, rule, validator):

    rule = CreationPolicy()
    errors = list(
        rule.validate(
            validator=validator,
            dP="creationpolicy",
            instance=instance,
            schema={},
        )
    )

    assert errors == expected, f"{name}: {errors} != {expected}"
