"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

import pytest

from cfnlint.api import ManualArgs, lint

# A full lint, because I7002 is only reached when E7001 wires in its child rules.

_RULE_IDS = ("E7002", "I7002")


def _template(mappings):
    template = {"Resources": {"Topic": {"Type": "AWS::SNS::Topic"}}}
    if mappings is not None:
        template["Mappings"] = mappings
    return template


def _approaching(name):
    return ("I7002", f"{name!r} is approaching the max length of 255")


def _longer(name):
    return ("E7002", f"{name!r} is longer than 255")


@pytest.mark.parametrize(
    "name,mappings,expected",
    [
        ("No Mappings section", None, []),
        ("Short names", {"MyMapping": {"us-east-1": {"Name": "one"}}}, []),
        (
            "Mapping name just under the threshold",
            {"M" * 229: {"us-east-1": {"Name": "one"}}},
            [],
        ),
        (
            "Mapping name just over the threshold",
            {"M" * 230: {"us-east-1": {"Name": "one"}}},
            [_approaching("M" * 230)],
        ),
        (
            "Mapping name at the limit",
            {"M" * 255: {"us-east-1": {"Name": "one"}}},
            [_approaching("M" * 255)],
        ),
        (
            "Mapping name over the limit",
            {"M" * 256: {"us-east-1": {"Name": "one"}}},
            [_longer("M" * 256)],
        ),
        (
            "Attribute name just under the threshold",
            {"MyMapping": {"us-east-1": {"A" * 229: "one"}}},
            [],
        ),
        (
            "Attribute name just over the threshold",
            {"MyMapping": {"us-east-1": {"A" * 230: "one"}}},
            [_approaching("A" * 230)],
        ),
        (
            "Attribute name at the limit",
            {"MyMapping": {"us-east-1": {"A" * 255: "one"}}},
            [_approaching("A" * 255)],
        ),
        (
            "Attribute name over the limit",
            {"MyMapping": {"us-east-1": {"A" * 256: "one"}}},
            [_longer("A" * 256)],
        ),
    ],
)
def test_mapping_name_length(name, mappings, expected):
    matches = lint(
        json.dumps(_template(mappings)),
        config=ManualArgs(regions=["us-east-1"], include_checks=["I"]),
    )

    assert [
        (match.rule.id, match.message)
        for match in matches
        if match.rule.id in _RULE_IDS
    ] == expected, f"Test {name!r} failed with {matches!r}"
