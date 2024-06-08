"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context, Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.SnapStart import SnapStart


@pytest.fixture(scope="module")
def rule():
    rule = SnapStart()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "GoodSnapStart": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {"S3Bucket": "XXXXXX", "S3Key": "key"},
                    "Handler": "handler",
                    "Role": "role",
                    "Runtime": "runtime",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                },
            },
            "GoodSnapStartVersion": {
                "Type": "AWS::Lambda::Version",
                "Properties": {"FunctionName": {"Ref": "GoodSnapStart"}},
            },
            "BadSnapStart": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {"S3Bucket": "XXXXXX", "S3Key": "key"},
                    "Handler": "handler",
                    "Role": "role",
                    "Runtime": "runtime",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                },
            },
        }
    }


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "None type should result in no errors",
            "None",  # Not
            deque(["Resources", "BadSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            [],
        ),
        (
            "Wrong type should result in no errors",
            [],  # wrong type
            deque(["Resources", "BadSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            [],
        ),
        (
            "Correctly associated version to lambda function",
            "PublishedVersions",
            deque(["Resources", "GoodSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            [],
        ),
        (
            "Lambda function doesn't have version attached",
            "PublishedVersions",
            deque(["Resources", "BadSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            [
                ValidationError(
                    (
                        "'SnapStart' is enabled but an 'AWS::Lambda::Version' "
                        "resource is not attached"
                    ),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, validator):
    validator = validator.evolve(
        context=Context(
            path=Path(
                path=path,
                cfn_path=deque(
                    [
                        "Resources",
                        "AWS::Lambda::Function",
                        "Properties",
                        "SnapStart",
                        "ApplyOn",
                    ]
                ),
            )
        )
    )
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"{name!r}: expected {expected!r} got {errs!r}"
