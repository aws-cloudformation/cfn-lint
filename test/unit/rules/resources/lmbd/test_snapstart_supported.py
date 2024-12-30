"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest import mock

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.SnapStartSupported import SnapStartSupported


@pytest.fixture(scope="module")
def rule():
    rule = SnapStartSupported()
    yield rule


@pytest.mark.parametrize(
    "name,instance,regions,add_child_rule,child_rule_called,expected",
    [
        (
            "SnapStart enabled on appropriate java version",
            {
                "Runtime": "java17",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [],
        ),
        (
            "SnapStart enabled with ref for runtime",
            {
                "Runtime": {"Ref": "Runtime"},
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [],
        ),
        (
            "SnapStart not enabled in region that doesn't support it",
            {
                "Runtime": "java17",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1", "foo-bar-1"],
            True,
            False,
            [
                ValidationError(
                    "'SnapStart' enabled functions are not supported in ['foo-bar-1']",
                    path=deque(["SnapStart", "ApplyOn"]),
                )
            ],
        ),
        (
            "SnapStart enabled for python3.12 error",
            {
                "Runtime": "python3.12",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [],
        ),
        (
            "SnapStart enabled for dotnet",
            {
                "Runtime": "dotnet8",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [],
        ),
        (
            "SnapStart enabled for go that isn't supported",
            {
                "Runtime": "go1.x",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [
                ValidationError(
                    "'go1.x' is not supported for 'SnapStart' enabled functions",
                    path=deque(["SnapStart", "ApplyOn"]),
                )
            ],
        ),
        (
            "SnapStart enabled for dotnet version that isn't supported",
            {
                "Runtime": "dotnet5.0",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [
                ValidationError(
                    "'dotnet5.0' is not supported for 'SnapStart' enabled functions",
                    path=deque(["SnapStart", "ApplyOn"]),
                )
            ],
        ),
        (
            "SnapStart enabled for dotnetcore version that isn't supported",
            {
                "Runtime": "dotnetcore2.1",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [
                ValidationError(
                    (
                        "'dotnetcore2.1' is not supported for "
                        "'SnapStart' enabled functions"
                    ),
                    path=deque(["SnapStart", "ApplyOn"]),
                )
            ],
        ),
        (
            "SnapStart not enabled on python non supported runtime",
            {
                "Runtime": "python3.11",
            },
            ["us-east-1"],
            True,
            True,
            [],
        ),
        (
            "SnapStart not enabled on python runtime in a bad region",
            {
                "Runtime": "python3.11",
            },
            ["foo-bar-1"],
            True,
            False,
            [],
        ),
        (
            "SnapStart not enabled and no child rule",
            {
                "Runtime": "java17",
            },
            ["us-east-1"],
            False,
            False,
            [],
        ),
        (
            "SnapStart set off with Python runtime",
            {
                "Runtime": "python3.11",
                "SnapStart": {
                    "ApplyOn": "None",
                },
            },
            ["us-east-1"],
            True,
            False,
            [],
        ),
        (
            "Snapstart should not be enabled for non java runtime",
            {
                "Runtime": "python3.11",
                "SnapStart": {
                    "ApplyOn": "PublishedVersions",
                },
            },
            ["us-east-1"],
            True,
            False,
            [
                ValidationError(
                    "'python3.11' is not supported for 'SnapStart' enabled functions",
                    path=deque(["SnapStart", "ApplyOn"]),
                )
            ],
        ),
    ],
)
def test_validate(
    name,
    instance,
    regions,
    add_child_rule,
    child_rule_called,
    expected,
    rule,
    validator,
):
    validator = validator.evolve(
        context=validator.context.evolve(regions=regions),
    )

    child_rule = mock.MagicMock()
    if add_child_rule:
        rule.child_rules["I2530"] = child_rule
    else:
        rule.child_rules["I2530"] = None

    errs = list(rule.validate(validator, "", instance, {}))

    if child_rule_called:
        child_rule.validate.assert_called_with(
            instance.get("Runtime")
        ), f"{name!r}: child rule not called"
    else:
        child_rule.validate.assert_not_called(), f"{name!r}: child rule called"

    assert errs == expected, f"{name!r}: expected {expected!r} got {errs!r}"
