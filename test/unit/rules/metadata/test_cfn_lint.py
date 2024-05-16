"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.metadata.CfnLint import CfnLint


@pytest.fixture(scope="module")
def rule():
    rule = CfnLint()
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
            "Valid cfn-lint config",
            {"config": {"ignore_checks": ["E3002"]}},
            [],
        ),
        (
            "Extra properties",
            {"config": {"ignore_bad_key": ["E3002"]}},
            [
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "('ignore_bad_key' was unexpected)"
                    ),
                    validator="additionalProperties",
                    schema_path=deque(["properties", "config", "additionalProperties"]),
                    rule=CfnLint(),
                    path=deque(["config", "ignore_bad_key"]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
