"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.formats import FormatKeyword
from cfnlint.rules.formats.Format import Format


@pytest.fixture(scope="module")
def rule():
    rule = Format()
    yield rule


class _Pass(FormatKeyword):
    id = "AAAAA"

    def __init__(self):
        super().__init__(format="test")

    def format(self, validator, instance):
        return True


class _Fail(FormatKeyword):
    id = "BBBBB"

    def __init__(self):
        super().__init__(format="test")

    def format(self, validator, instance):
        return False


class _FailWithPattern(FormatKeyword):
    id = "BBBBB"

    def __init__(self):
        super().__init__(format="test", pattern=r"^.*$")

    def format(self, validator, instance):
        return False


class _NoRuleId(FormatKeyword):
    def __init__(self):
        super().__init__(format="test")

    def format(self, validator, instance):
        return False


@pytest.mark.parametrize(
    "name,format,instance,child_rules,expected",
    [
        (
            "Standard format",
            "ipv4",
            "10.10.10.10",
            [],
            [],
        ),
        (
            "Bad standard format",
            "ipv4",
            "10.10.10",
            [],
            [
                ValidationError(
                    "'10.10.10' is not a 'ipv4'",
                )
            ],
        ),
        (
            "Pass format type",
            "test",
            "10.10.10.10",
            {
                "AAAAA": _Pass(),
            },
            [],
        ),
        (
            "Child rule empty",
            "test",
            "10.10.10.10",
            {
                "BBBBB": None,
            },
            [],
        ),
        (
            "No Rule ID",
            "test",
            "10.10.10.10",
            {
                "AAAAA": _NoRuleId(),
            },
            [],
        ),
        (
            "Fail with new format type",
            "test",
            "10.10.10.10",
            {
                "BBBBB": _Fail(),
            },
            [
                ValidationError(
                    "'10.10.10.10' is not a valid 'test'",
                    rule=_Fail(),
                )
            ],
        ),
        (
            "Fail with multiple rules",
            "test",
            "10.10.10.10",
            {
                "BBBBB": _Fail(),
                "AAAAA": _Pass(),
            },
            [
                ValidationError(
                    "'10.10.10.10' is not a valid 'test'",
                    rule=_Fail(),
                )
            ],
        ),
        (
            "Fail with pattern",
            "test",
            "10.10.10.10",
            {
                "AAAAA": _FailWithPattern(),
            },
            [
                ValidationError(
                    "'10.10.10.10' is not a 'test' with pattern '^.*$'",
                    rule=_FailWithPattern(),
                )
            ],
        ),
    ],
)
def test_validate(name, format, instance, child_rules, expected, rule, validator):
    rule.child_rules = child_rules
    result = list(rule.format(validator, format, instance, {}))
    assert result == expected, f"Test {name!r} got {result!r}"
