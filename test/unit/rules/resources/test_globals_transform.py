"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.rules.resources.GlobalsTransform import GlobalsTransform


@pytest.fixture(scope="module")
def rule():
    yield GlobalsTransform()


@pytest.mark.parametrize(
    "name,instance,template,path,expected",
    [
        (
            "Valid globals with transform",
            {"Function": {"Runtime": "python3.12"}},
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {"cfn_path": deque(["Globals"])},
            0,
        ),
        (
            "Globals without transform",
            {"Function": {"Runtime": "python3.12"}},
            {},
            {"cfn_path": deque(["Globals"])},
            1,
        ),
        (
            "Non-dict instance",
            "not-a-dict",
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {"cfn_path": deque(["Globals"])},
            0,
        ),
        (
            "Invalid globals property",
            {"Function": {"Runtime": "python3.12"}, "InvalidKey": {}},
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {"cfn_path": deque(["Globals"])},
            1,
        ),
    ],
    indirect=["template", "path"],
)
def test_validate(name, instance, template, path, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    assert len(errors) == expected, f"Test {name!r} got {errors!r}"
