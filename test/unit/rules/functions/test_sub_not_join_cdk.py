"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.functions.SubNotJoin import SubNotJoin


@pytest.fixture(scope="module")
def rule():
    rule = SubNotJoin()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyResource": {
                "Type": "AWS::S3::Bucket",
            },
            "CDK": {
                "Type": "AWS::CDK::Metadata",
            },
        },
    }


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Invalid Fn::Join with an empty string",
            {"Fn::Join": ["", ["foo", "bar"]]},
            {"type": "string"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
