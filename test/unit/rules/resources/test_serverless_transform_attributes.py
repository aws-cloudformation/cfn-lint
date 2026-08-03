"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.rules.resources.ServerlessTransformAttributes import (
    ServerlessTransformAttributes,
)


@pytest.fixture(scope="module")
def rule():
    yield ServerlessTransformAttributes()


@pytest.mark.parametrize(
    "name,instance,template,path,expected",
    [
        (
            "Connectors without transform",
            {"MyConn": {"Properties": {"Destination": {"Id": "Table"}}}},
            {},
            {
                "cfn_path": deque(["Resources", "Fn", "Connectors"]),
                "path": deque(["Resources", "Fn", "Connectors"]),
            },
            1,
        ),
        (
            "Connectors with transform",
            {"MyConn": {"Properties": {"Destination": {"Id": "Table"}}}},
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {
                "cfn_path": deque(["Resources", "Fn", "Connectors"]),
                "path": deque(["Resources", "Fn", "Connectors"]),
            },
            0,
        ),
        (
            "IgnoreGlobals without transform",
            ["Runtime"],
            {},
            {
                "cfn_path": deque(["Resources", "Fn", "IgnoreGlobals"]),
                "path": deque(["Resources", "Fn", "IgnoreGlobals"]),
            },
            1,
        ),
        (
            "IgnoreGlobals with transform",
            ["Runtime"],
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {
                "cfn_path": deque(["Resources", "Fn", "IgnoreGlobals"]),
                "path": deque(["Resources", "Fn", "IgnoreGlobals"]),
            },
            0,
        ),
    ],
    indirect=["template", "path"],
)
def test_validate(name, instance, template, path, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    assert len(errors) == expected, f"Test {name!r} got {errors!r}"
