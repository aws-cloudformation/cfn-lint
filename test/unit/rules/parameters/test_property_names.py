"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

import pytest

from cfnlint.api import ManualArgs, lint

# A full lint, because I2011 is only reached when E2001 wires in its child rules.

_RULE_IDS = ("E2001", "E2011", "I2011")


def _template(parameters):
    template = {"Resources": {"Topic": {"Type": "AWS::SNS::Topic"}}}
    if parameters is not None:
        template["Parameters"] = parameters
    return template


def _approaching(name):
    return ("I2011", f"{name!r} is approaching the max length of 255")


def _longer(name):
    return ("E2011", f"{name!r} is longer than 255")


# E2001 is only checked for attribution; its message lists every parameter attribute.
_E2001 = ("E2001", None)


def _key(match):
    if match.rule.id == "E2001":
        return _E2001
    return (match.rule.id, match.message)


@pytest.mark.parametrize(
    "name,parameters,expected",
    [
        ("No Parameters section", None, []),
        ("Short name", {"MyParameter": {"Type": "String"}}, []),
        ("Just under the threshold", {"P" * 229: {"Type": "String"}}, []),
        (
            "Just over the threshold",
            {"P" * 230: {"Type": "String"}},
            [_approaching("P" * 230)],
        ),
        (
            "At the limit",
            {"P" * 255: {"Type": "String"}},
            [_approaching("P" * 255)],
        ),
        (
            "Over the limit",
            {"P" * 256: {"Type": "String"}},
            [_longer("P" * 256)],
        ),
        (
            "Unknown attribute on a long name is still reported by E2001",
            {"P" * 240: {"Type": "String", "Foo": "bar"}},
            [_E2001, _E2001, _approaching("P" * 240)],
        ),
    ],
)
def test_parameter_name_length(name, parameters, expected):
    matches = lint(
        json.dumps(_template(parameters)),
        config=ManualArgs(regions=["us-east-1"], include_checks=["I"]),
    )

    assert [
        _key(match) for match in matches if match.rule.id in _RULE_IDS
    ] == expected, f"Test {name!r} failed with {matches!r}"
