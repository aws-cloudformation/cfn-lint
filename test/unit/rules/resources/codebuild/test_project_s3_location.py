"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.codebuild.ProjectS3Location import ProjectS3Location


@pytest.fixture(scope="module")
def rule():
    rule = ProjectS3Location()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Type": "S3",
                "Location": "path",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "Type": {"Ref": "AWS::StackName"},  # not a string
                "Location": "path",
            },
            [],
        ),
        (
            {
                "Type": "S3",
            },
            [
                ValidationError(
                    "'Location' is a required property when using 'Type' of 'S3'",
                    rule=ProjectS3Location(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
