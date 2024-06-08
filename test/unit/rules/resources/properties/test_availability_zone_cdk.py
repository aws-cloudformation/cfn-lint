"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.rules.resources.properties.AvailabilityZone import (
    AvailabilityZone,  # pylint: disable=E0401
)


@pytest.fixture(scope="module")
def rule():
    rule = AvailabilityZone()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MySqs": {
                "Type": "AWS::SQS::Queue",
            },
            "CDK": {
                "Type": "AWS::CDK::Metadata",
            },
        }
    }


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid hardcoded string because CDK",
            "us-east-1a",
            {
                "path": deque(["Resources", "MySqs", "Properties"]),
            },
            [],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, path, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert errors == expected, f"Test {name!r} got {errors!r}"
