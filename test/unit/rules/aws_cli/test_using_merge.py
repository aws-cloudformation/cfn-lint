"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.decode.cfn_yaml import loads
from cfnlint.rules import RuleMatch
from cfnlint.rules.aws_cli.UsingMerge import UsingMerge


@pytest.fixture(scope="module")
def rule():
    rule = UsingMerge()
    yield rule


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,template,expected",
    [
        (
            "A good template",
            loads(
                """
            One:
                A: 1
            """
            ),
            [],
        ),
        (
            "A merge template",
            loads(
                """
            One:
                &foo
                A: 1
            Two:
                <<: *foo
                A: 2
            """
            ),
            [
                RuleMatch(
                    path=["Two"],
                    message=(
                        "This code is using yaml marge capabilities "
                        "and can only be deployed using the "
                        "'package' cli command"
                    ),
                )
            ],
        ),
    ],
    indirect=["template"],
)
def test_validate(name, template, expected, rule, cfn):
    errs = list(rule.match(cfn))

    assert errs == expected, f"Test {name!r} got {errs!r}"
