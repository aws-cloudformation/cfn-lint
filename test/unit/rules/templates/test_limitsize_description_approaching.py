"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.templates.ApproachingLimitDescription import (
    ApproachingLimitDescription,
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = ApproachingLimitDescription()
    yield rule


@pytest.fixture(scope="module")
def validator():
    cfn = Template("", {})
    context = create_context_for_template(cfn)
    yield CfnTemplateValidator(schema={}, context=context, cfn=cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid description",
            "a" * 18,
            [],
        ),
        (
            "Too long",
            "a" * 19,
            [
                ValidationError(
                    f"'{'a'*19}' is approaching the max length of 20",
                    rule=ApproachingLimitDescription(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errors = list(rule.maxLength(validator, 20, instance, {}))

    assert errors == expected, f"Test {name!r} got {errors!r}"
