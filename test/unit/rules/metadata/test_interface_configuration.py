"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.metadata.InterfaceConfiguration import InterfaceConfiguration


@pytest.fixture(scope="module")
def rule():
    rule = InterfaceConfiguration()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        resources={},
        parameters={
            "Foo": Parameter({"Type": "String"}),
            "Bar": Parameter({"Type": "String"}),
        },
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Interface",
            {
                "ParameterGroups": [
                    {
                        "Label": "A Group",
                        "Parameters": [
                            "Foo",
                            "Bar",
                        ],
                    }
                ],
                "ParameterLabels": {"Foo": {"default": "a parameter"}},
            },
            [],
        ),
        (
            "Extra properties",
            {"Foo": "Bar"},
            [
                ValidationError(
                    ("Additional properties are not allowed " "('Foo' was unexpected)"),
                    validator="additionalProperties",
                    schema_path=deque(["additionalProperties"]),
                    rule=InterfaceConfiguration(),
                    path=deque(["Foo"]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
