"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.rules.parameters.NumberRange import NumberRange as ParamaterNumberRange
from cfnlint.rules.resources.properties.NumberRange import NumberRange


@pytest.fixture
def rule():
    rule = NumberRange()
    rule.child_rules["W3034"] = ParamaterNumberRange()
    yield NumberRange()


def test_minimum(rule, validator):
    assert len(list(rule.minimum(validator, 1, 1, {}))) == 0
    assert len(list(rule.minimum(validator, 1, 0, {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Ref"]),
                value_path=deque(["Parameters", "MyParameter", "MinValue"]),
            )
        )
    )
    errs = list(rule.minimum(evolved, 1, 0, {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParamaterNumberRange.id

    rule.child_rules["W3034"] = None
    errs = list(rule.minimum(evolved, 1, 0, {}))
    assert len(errs) == 0


def test_maximum(rule, validator):
    assert len(list(rule.maximum(validator, 1, 1, {}))) == 0
    assert len(list(rule.maximum(validator, 1, 2, {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Ref"]),
                value_path=deque(["Parameters", "MyParameter", "MinValue"]),
            ),
        )
    )
    errs = list(rule.maximum(evolved, 1, 2, {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParamaterNumberRange.id

    rule.child_rules["W3034"] = None
    errs = list(rule.maximum(evolved, 1, 2, {}))
    assert len(errs) == 0


def test_exclusive_minimum(rule, validator):
    assert len(list(rule.exclusiveMinimum(validator, 1, 2, {}))) == 0
    assert len(list(rule.exclusiveMinimum(validator, 1, 1, {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Ref"]),
                value_path=deque(["Parameters", "MyParameter", "MinValue"]),
            ),
        )
    )
    errs = list(rule.exclusiveMinimum(evolved, 1, 1, {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParamaterNumberRange.id

    rule.child_rules["W3034"] = None
    errs = list(rule.exclusiveMinimum(evolved, 1, 1, {}))
    assert len(errs) == 0


def test_exlusive_maximum(rule, validator):
    assert len(list(rule.exclusiveMaximum(validator, 1, 0, {}))) == 0
    assert len(list(rule.exclusiveMaximum(validator, 1, 1, {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Ref"]),
                value_path=deque(["Parameters", "MyParameter", "MinValue"]),
            ),
        )
    )
    errs = list(rule.exclusiveMaximum(evolved, 1, 1, {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParamaterNumberRange.id

    rule.child_rules["W3034"] = None
    errs = list(rule.exclusiveMaximum(evolved, 1, 1, {}))
    assert len(errs) == 0
