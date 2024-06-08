"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.Condition import Condition
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Condition()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Conditions": {
                "MyCondition": {"Fn::Equals": [{"Ref": "MyParam"}, "Foo"]},
            },
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Condition is valid",
            "MyCondition",
            [],
        ),
        (
            "Valid because of wrong type",
            {},
            [],
        ),
        (
            "Invalid condition",
            "IsProduction",
            [
                ValidationError(
                    "'IsProduction' is not one of ['MyCondition']",
                    validator="enum",
                    schema_path=deque(["enum"]),
                    rule=Condition(),
                    path=deque([]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
