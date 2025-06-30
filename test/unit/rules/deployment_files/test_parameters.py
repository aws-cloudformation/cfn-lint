"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import ParameterSet
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.deployment_files.Parameters import Parameters


@pytest.fixture(scope="module")
def rule():
    rule = Parameters()
    yield rule


@pytest.mark.parametrize(
    "name,instance,parameters,expected",
    [
        (
            "None is okay",
            {"Foo": {"Type": "String"}},
            None,
            [],
        ),
        (
            "Parameter provided with no default",
            {"Foo": {"Type": "String"}},
            [
                ParameterSet(
                    source=None,
                    parameters={
                        "Foo": "Bar",
                    },
                )
            ],
            [],
        ),
        (
            "Empty is okay because parameter has default",
            {"Foo": {"Type": "String", "Default": "Bar"}},
            {},
            [],
        ),
        (
            "Empty with no default should have an error",
            {"Foo": {"Type": "String"}},
            [ParameterSet(source=None, parameters={})],
            [
                ValidationError(
                    "'Foo' is a required property",
                    path=[],
                    validator="required",
                    schema_path=deque(["required"]),
                    rule=Parameters(),
                )
            ],
        ),
        (
            "Failure on bad enum",
            {"Foo": {"Type": "String", "AllowedValues": ["A", "B", "C"]}},
            [ParameterSet(source=None, parameters={"Foo": "D"})],
            [
                ValidationError(
                    "'D' is not one of ['A', 'B', 'C']",
                    path=deque(["Foo"]),
                    validator="enum",
                    schema_path=deque(["properties", "Foo", "enum"]),
                    rule=Parameters(),
                )
            ],
        ),
        (
            "Failure on bad pattern",
            {"Foo": {"Type": "String", "Pattern": "^Bar$"}},
            [ParameterSet(source=None, parameters={"Foo": "D"})],
            [
                ValidationError(
                    "'D' does not match '^Bar$'",
                    path=deque(["Foo"]),
                    validator="pattern",
                    schema_path=deque(["properties", "Foo", "pattern"]),
                    rule=Parameters(),
                )
            ],
        ),
        (
            "Okay with a list",
            {"Foo": {"Type": "CommaDelimitedList"}},
            [ParameterSet(source=None, parameters={"Foo": ["D"]})],
            [],
        ),
        (
            "Not okay with a list and a bad pattern",
            {"Foo": {"Type": "CommaDelimitedList", "Pattern": "^Bar$"}},
            [ParameterSet(source=None, parameters={"Foo": ["Bar", "D"]})],
            [
                ValidationError(
                    "'D' does not match '^Bar$'",
                    path=deque(["Foo", 1]),
                    validator="pattern",
                    schema_path=deque(["properties", "Foo", "items", "pattern"]),
                    rule=Parameters(),
                )
            ],
        ),
        (
            "Not okay with a list and an enum",
            {"Foo": {"Type": "CommaDelimitedList", "AllowedValues": ["Bar"]}},
            [ParameterSet(source=None, parameters={"Foo": ["Bar", "D"]})],
            [
                ValidationError(
                    "'D' is not one of ['Bar']",
                    path=deque(["Foo", 1]),
                    validator="enum",
                    schema_path=deque(["properties", "Foo", "items", "enum"]),
                    rule=Parameters(),
                )
            ],
        ),
        (
            "No issues when a bad property type",
            [{"Foo": {"Type": "CommaDelimitedList", "AllowedValues": ["Bar"]}}],
            [ParameterSet(source=None, parameters={"Foo": "Bar"})],
            [],
        ),
        (
            "No issues when a bad property type",
            {"Foo": [{"Type": "CommaDelimitedList", "AllowedValues": ["Bar"]}]},
            [ParameterSet(source=None, parameters={"Foo": "Bar"})],
            [],
        ),
        (
            "No issues when a bad type",
            {"Foo": {"Type": ["String"], "AllowedValues": ["Bar"]}},
            [ParameterSet(source=None, parameters={"Foo": "Foo"})],
            [],
        ),
    ],
    indirect=["parameters"],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
