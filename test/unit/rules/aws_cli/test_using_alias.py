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


def _alias_message(name):
    return (
        f"YAML alias '*{name}' is rejected by CloudFormation unless the "
        "template is first processed by the 'package' cli command or AWS SAM"
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
            "An anchor without an alias",
            loads(
                """
            One: &foo
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
                    message=_alias_message("foo"),
                )
            ],
        ),
        (
            "An alias used more than once is reported at each use",
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
                    message=_alias_message("foo"),
                ),
                RuleMatch(
                    path=["Three"],
                    message=_alias_message("foo"),
                ),
            ],
        ),
        (
            "A scalar alias",
            loads(
                """
            Resources:
                FirstLogGroup:
                    Type: AWS::Logs::LogGroup
                    Properties:
                        RetentionInDays: &Retention 30
                SecondLogGroup:
                    Type: AWS::Logs::LogGroup
                    Properties:
                        RetentionInDays: *Retention
            """
            ),
            [
                RuleMatch(
                    path=[
                        "Resources",
                        "SecondLogGroup",
                        "Properties",
                        "RetentionInDays",
                    ],
                    message=_alias_message("Retention"),
                )
            ],
        ),
        (
            "An alias in a sequence",
            loads(
                """
            One: &foo bar
            Two:
                - *foo
            Three: [baz, *foo]
            """
            ),
            [
                RuleMatch(
                    path=["Two"],
                    message=_alias_message("foo"),
                ),
                RuleMatch(
                    path=["Three"],
                    message=_alias_message("foo"),
                ),
            ],
        ),
        (
            "An alias in a merge key",
            loads(
                """
            One: &foo
                A: 1
            Two:
                <<: *foo
                B: 2
            """
            ),
            [
                RuleMatch(
                    path=["Two"],
                    message=_alias_message("foo"),
                )
            ],
        ),
        (
            "A SAM template is deployed with the SAM CLI",
            loads(
                """
            Transform: AWS::Serverless-2016-10-31
            One: &foo 30
            Two: *foo
            """
            ),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(name, template, expected, rule, cfn):
    errs = list(rule.match(cfn))

    assert errs == expected, f"Test {name!r} got {errs!r}"


@pytest.mark.parametrize(
    "template",
    [
        loads(
            """
        One: &foo 30
        Two:
            Three: *foo
        """
        )
    ],
    indirect=["template"],
)
def test_location(template, rule, cfn):
    (err,) = rule.match(cfn)

    # Zero-based line and column of the alias itself, not of its anchor
    assert err.location == (3, 19, 3, 23)
