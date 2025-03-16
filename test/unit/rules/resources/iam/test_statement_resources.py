"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.iam.StatementResources import StatementResources, _Arn


@pytest.fixture(scope="module")
def rule():
    rule = StatementResources()
    yield rule


def template():
    return {
        "Resources": {
            "LogGroup": {
                "Type": "AWS::Logs::LogGroup",
            }
        }
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": "*",
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["*"],
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": "*",
            },
            [],
        ),
        (
            # action with no colon
            {
                "Action": ["cloudformationCreateStackSet"],
                "Resource": "arn",
            },
            [],
        ),
        (
            # service not in map
            {
                "Action": ["foo:CreateStackSet"],
                "Resource": "arn",
            },
            [],
        ),
        (
            # action not in map
            {
                "Action": ["cloudformation:foo"],
                "Resource": "arn",
            },
            [],
        ),
        (
            # skip validation on asterisk actions
            {
                "Action": ["foo:Create*"],
                "Resource": "arn",
            },
            [],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": "arn",
            },
            [
                ValidationError(
                    "action 'cloudformation:CreateStackSet' requires a resource of '*'",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["arn"],
            },
            [
                ValidationError(
                    "action 'cloudformation:CreateStackSet' requires a resource of '*'",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["arn", "*"],
            },
            [],
        ),
        (
            {
                "Action": [
                    "cloudformation:CreateStackSet",
                    "cloudformation:CreateStack",
                ],
                "Resource": ["arn:aws:cloudformation:*:*:stack/*"],
            },
            [
                ValidationError(
                    "action 'cloudformation:CreateStackSet' requires a resource of '*'",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:stack/*"],
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": [
                    "arn:aws:cloudformation:us-east-1:123456789012:stack/dne/*"
                ],
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": ["arn:aws:logs:us-east-1:123456789012:stack/dne/*"],
            },
            [
                ValidationError(
                    (
                        "action 'cloudformation:CreateStack' "
                        "requires a resource of "
                        "['arn:${Partition}:cloudformation:${Region}:${Account}:stack/.*']"
                    ),
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": ["arn:aws:logs:us-east-1:123456789012:stack/dne/*"],
            },
            [
                ValidationError(
                    (
                        "action 'cloudformation:CreateStack' "
                        "requires a resource of "
                        "['arn:${Partition}:cloudformation:${Region}:${Account}:stack/.*']"
                    ),
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
        (
            {
                "Action": "logs:CreateLogGroup",
                "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:dne",
            },
            [],
        ),
        (
            {
                "Action": "logs:CreateLogGroup",
                "Resource": "arn:aws:logs:us-east-1:123456789012:log-group*",
            },
            [],
        ),
        (
            {
                "Action": [
                    "cloudformation:CreateStack",
                    "logs:CreateLogGroup",
                ],
                "Resource": [
                    "arn:aws:cloudformation:us-east-1:123456789012:stack/dne/*",
                    "arn:aws:logs:us-east-1:123456789012:log-group:dne",
                ],
            },
            [],
        ),
        (
            {
                "Action": [
                    "cloudformation:CreateStack",
                    "logs:CreateLogGroup",
                ],
                "Resource": [
                    "arn:aws:cloudformation:us-east-1:123456789012:changeSet/dne/*",
                    "arn:aws:logs:us-east-1:123456789012:log-group:dne",
                ],
            },
            [
                ValidationError(
                    (
                        "action 'cloudformation:CreateStack' requires "
                        "a resource of "
                        "['arn:${Partition}:cloudformation:${Region}:${Account}:stack/.*']"
                    ),
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
        (
            # should not fail on the actions that require a resource
            # but still fails because there is no asterisk
            {
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams",
                ],
                "Resource": {"Fn::GetAtt": "LogGroup.Arn"},
            },
            [
                ValidationError(
                    "action 'logs:DescribeLogGroups' requires a resource of '*'",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                ),
            ],
        ),
    ],
)
def test_rule(instance, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))

    assert errors == expected, f"Got {errors!r}"


def test_added():
    arn = _Arn("arn:aws:cloudformation:us-east-1:123456789012:stack/*")

    assert arn.__repr__() == "arn:aws:cloudformation:us-east-1:123456789012:stack/*"
    assert arn != 1
