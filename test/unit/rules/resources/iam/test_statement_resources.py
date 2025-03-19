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


@pytest.fixture
def template():
    return {
        "Parameters": {
            "MyParameter": {"Type": "String"},
        },
        "Resources": {
            "LogGroup": {
                "Type": "AWS::Logs::LogGroup",
            }
        },
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
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            # service not in map
            {
                "Action": ["foo:CreateStackSet"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            # action not in map
            {
                "Action": ["cloudformation:foo"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            # skip validation on asterisk actions
            {
                "Action": ["foo:Create*"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            {
                "Action": [{"Ref": "MyParameter"}],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            {
                "Action": {"Ref": "MyParameter"},
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": [{"Ref": "MyParameter"}],
            },
            [],
        ),
        (
            {
                "Action": "ec2:CreateTags",
                "Resource": ["arn:aws:ec2:*::snapshot/*"],
            },
            [],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": [{"Ref": "LogGroup"}],
            },
            [
                # ValidationError(
                #    "action 'cloudformation:CreateStackSet' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
            ],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": [{"Foo": "Bar"}],
            },
            [
                # ValidationError(
                #    "action 'cloudformation:CreateStackSet' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
            ],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [
                # ValidationError(
                #    "action 'cloudformation:CreateStackSet' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
            ],
        ),
        (
            {
                "Action": [
                    "cloudformation:CreateStackSet",
                    {"Ref": "MyParameter"},
                ],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [
                # ValidationError(
                #    "action 'cloudformation:CreateStackSet' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*"],
            },
            [
                # ValidationError(
                #    "action 'cloudformation:CreateStackSet' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*", "*"],
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
                # ValidationError(
                #    "action 'cloudformation:CreateStackSet' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
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
                "Resource": ["arn:aws:cloudformation:us-east-1:123456789012:*dne*"],
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
                "Action": ["cloudformation:Create?tack"],
                "Resource": ["arn:aws:logs:us-east-1:123456789012:stack/dne/*"],
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
            # no delimiter in resource
            {
                "Action": [
                    "codepipeline:putapprovalresult",
                ],
                "Resource": [
                    "arn:aws:codepipeline:us-east-1:123456789012:resource-name",
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
                # ValidationError(
                #    "action 'logs:DescribeLogGroups' requires a resource of '*'",  # noqa: E501
                #    rule=StatementResources(),
                #    path=deque(["Resource"]),
                # ),
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

    greengress_1 = _Arn(
        "arn:aws:cloudformation:us-east-1:123456789012:/greengrass/definition/connectors/.*"
    )
    greengress_2 = _Arn("arn:aws:cloudformation:us-east-1:123456789012:/greengrass")
    greengrass_3 = _Arn(
        "arn:aws:cloudformation:us-east-1:123456789012:/greengrass/things/"
    )

    assert greengress_1 == greengress_2
    assert greengress_1 != greengrass_3

    assert _Arn("arn:aws:cloudformation:us-east-1:123456789012:") == _Arn(
        "arn:aws:cloudformation:us-east-1:123456789012:"
    )
    assert _Arn("arn:aws:cloudformation:us-east-1:123456789012:test/") == _Arn(
        "arn:aws:cloudformation:us-east-1:123456789012:test/"
    )
