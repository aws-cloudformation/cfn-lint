"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.decode.cfn_yaml import loads
from cfnlint.rules import RuleMatch
from cfnlint.rules.aws_cli.UsingAlias import UsingAlias


@pytest.fixture(scope="module")
def rule():
    rule = UsingAlias()
    yield rule


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


_ALIAS_MESSAGE = (
    "This code is using a YAML alias and can only "
    "be deployed using the 'package' cli command "
    "or AWS SAM"
)


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
            "An alias template",
            loads(
                """
            One:
                &foo
                A: 1
            Two: *foo
            """
            ),
            [
                RuleMatch(
                    path=["Two"],
                    message=_ALIAS_MESSAGE,
                )
            ],
        ),
        (
            "An alias used more than once is reported once",
            loads(
                """
            One:
                &foo
                A: 1
            Two: *foo
            Three: *foo
            """
            ),
            [
                RuleMatch(
                    path=["Two"],
                    message=_ALIAS_MESSAGE,
                )
            ],
        ),
    ],
    indirect=["template"],
)
def test_validate(name, template, expected, rule, cfn):
    errs = list(rule.match(cfn))

    assert errs == expected, f"Test {name!r} got {errs!r}"
