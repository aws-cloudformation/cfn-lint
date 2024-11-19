"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.iam.Permissions import Permissions


@pytest.fixture(scope="module")
def rule():
    rule = Permissions()
    yield rule


@pytest.fixture
def template():
    return {
        "Transform": "AWS::Serverless-2016-10-31",
    }


@pytest.mark.parametrize(
    "name,instance,err_count",
    [
        ("Empty string", "", 0),
    ],
)
def test_permissions(name, instance, err_count, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))
    assert len(errors) == err_count, f"Test {name!r} got {errors!r}"
