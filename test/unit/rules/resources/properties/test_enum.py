"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.parameters.AllowedValue import AllowedValue as ParameterAllowedValue
from cfnlint.rules.resources.properties.Enum import Enum


@pytest.fixture(scope="module")
def rule():
    rule = Enum()
    rule.child_rules["W2030"] = ParameterAllowedValue()
    yield Enum()


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


def test_validate(rule, validator):
    assert len(list(rule.enum(validator, ["foo", "bar"], "foo", {}))) == 0
    assert len(list(rule.enum(validator, ["foo"], "bar", {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=deque(["Fn::Sub"]),
        )
    )
    errs = list(rule.enum(evolved, ["bar"], "bar", {}))
    assert len(errs) == 0

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=deque(["Ref"]),
            value_path=deque(["Parameters", "MyParameter", "Default"]),
        )
    )
    errs = list(rule.enum(evolved, ["foo"], "bar", {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParameterAllowedValue.id

    rule.child_rules["W2030"] = None
    errs = list(rule.enum(evolved, ["foo"], "bar", {}))
    assert len(errs) == 0
