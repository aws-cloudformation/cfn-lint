"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.rules.parameters.ValuePattern import ValuePattern as ParameterPattern
from cfnlint.rules.resources.properties.Pattern import Pattern


@pytest.fixture(scope="module")
def rule():
    rule = Pattern()
    rule.child_rules["W2031"] = ParameterPattern()
    yield rule


def test_validate(rule, validator):
    assert len(list(rule.pattern(validator, ".*", "foo", {}))) == 0
    assert len(list(rule.pattern(validator, "foo", "bar", {}))) == 1

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=Path(path=deque(["Fn::Sub"])),
        )
    )
    errs = list(rule.pattern(evolved, "bar", "bar", {}))
    assert len(errs) == 0

    evolved = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Ref"]),
                value_path=deque(["Parameters", "MyParameter", "Default"]),
            ),
        )
    )
    errs = list(rule.pattern(evolved, "foo", "bar", {}))
    assert len(errs) == 1
    assert errs[0].rule.id == ParameterPattern.id

    rule.child_rules["W2031"] = None
    errs = list(rule.pattern(evolved, "foo", "bar", {}))
    assert len(errs) == 0


def test_pattern_exceptions(rule, validator):
    rule.configure({"exceptions": ["AWS::"]})

    assert len(list(rule.pattern(validator, "foo", "Another AWS::Instance", {}))) == 1
    assert len(list(rule.pattern(validator, "foo", "AWS::Dummy::Resource", {}))) == 0


def test_is_exception_method(rule, validator):
    """Test the _is_exception method directly"""
    rule.configure({"exceptions": ["AWS::", "Test::"]})

    # Test with allow_exceptions=True (default behavior)
    validator_with_exceptions = validator.evolve(
        context=validator.context.evolve(allow_exceptions=True)
    )

    assert rule._is_exception(validator_with_exceptions, "AWS::EC2::Instance")
    assert rule._is_exception(validator_with_exceptions, "Test::Resource")
    assert not rule._is_exception(validator_with_exceptions, "Other::Resource")

    # Test with allow_exceptions=False
    validator_no_exceptions = validator.evolve(
        context=validator.context.evolve(allow_exceptions=False)
    )

    # All should return False when allow_exceptions=False, regardless of pattern match
    assert not rule._is_exception(validator_no_exceptions, "AWS::EC2::Instance")
    assert not rule._is_exception(validator_no_exceptions, "Test::Resource")
    assert not rule._is_exception(validator_no_exceptions, "Other::Resource")
