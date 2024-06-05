"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import Context
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.formats.SecurityGroupName import SecurityGroupName


@pytest.fixture(scope="module")
def rule():
    rule = SecurityGroupName()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        resources={},
        parameters={},
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid security group name",
            "aA0_-:/()#,@[]+=&;{}!$*zZ9",
            True,
        ),
        (
            "Valid with wrong type",
            [],
            True,
        ),
        ("Invalid security group name", "a?Z", False),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
