"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from collections import deque

import pytest

from cfnlint.context import Value, ValueType
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.parameters.AllowedValue import AllowedValue as ParameterAllowedValue
from cfnlint.rules.resources.properties.AllowedValue import AllowedValue


@pytest.fixture(scope="module")
def rule():
    rule = AllowedValue()
    rule.child_rules["W2030"] = ParameterAllowedValue()
    yield AllowedValue()


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


def test_allowed_value(rule, validator):
    assert len(list(rule.enum(validator, ["foo", "bar"], "foo", {}))) == 0
    assert len(list(rule.enum(validator, ["foo"], "bar", {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=deque(["Fn::Sub"]),
            value=Value(
                value="bar",
                value_type=ValueType.STANDARD,
                path=deque([]),
            ),
        )
    )
    errs = list(rule.enum(evolved, ["bar"], "bar", {}))
    assert len(errs) == 0

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=deque(["Ref"]),
            value=Value(
                value="bar",
                value_type=ValueType.FUNCTION,
                path=deque(["Parameters", "MyParameter", "Default"]),
            ),
        )
    )
    errs = list(rule.enum(evolved, ["foo"], "bar", {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParameterAllowedValue.id

    rule.child_rules["W2030"] = None
    errs = list(rule.enum(evolved, ["foo"], "bar", {}))
    assert len(errs) == 0
