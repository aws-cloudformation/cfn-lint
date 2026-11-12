"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.sns.SubscriptionFirehoseRole import (
    SubscriptionFirehoseRole,
)

_endpoint = "arn:aws:firehose:us-east-1:123456789012:deliverystream/stream"
_role = "arn:aws:iam::123456789012:role/sns-firehose"


@pytest.fixture(scope="module")
def rule():
    rule = SubscriptionFirehoseRole()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        # Valid: firehose with SubscriptionRoleArn
        (
            {
                "Protocol": "firehose",
                "Endpoint": _endpoint,
                "SubscriptionRoleArn": _role,
            },
            0,
            None,
        ),
        # Valid: firehose with SubscriptionRoleArn from a function
        (
            {
                "Protocol": "firehose",
                "Endpoint": _endpoint,
                "SubscriptionRoleArn": {"Fn::GetAtt": ["Role", "Arn"]},
            },
            0,
            None,
        ),
        # Valid: other protocols don't need SubscriptionRoleArn
        (
            {"Protocol": "sqs", "Endpoint": "arn:aws:sqs:us-east-1:123456789012:q"},
            0,
            None,
        ),
        # Valid: Protocol isn't known
        (
            {"Protocol": {"Ref": "Protocol"}, "Endpoint": _endpoint},
            0,
            None,
        ),
        # Valid: no Protocol is handled elsewhere
        (
            {"Endpoint": _endpoint},
            0,
            None,
        ),
        # Valid: wrong type is handled elsewhere
        (
            [],
            0,
            None,
        ),
        # Invalid: firehose without SubscriptionRoleArn
        (
            {"Protocol": "firehose", "Endpoint": _endpoint},
            1,
            (
                "'SubscriptionRoleArn' is a required property "
                "when 'Protocol' is 'firehose'"
            ),
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}: {errs!r}"
    )
    if expected_message:
        assert errs[0].message == expected_message
