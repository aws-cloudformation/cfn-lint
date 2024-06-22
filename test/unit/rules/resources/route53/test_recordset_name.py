"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.route53.RecordSetName import RecordSetName


@pytest.fixture(scope="module")
def rule():
    rule = RecordSetName()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "HostedZoneName": "bar.",
                "Name": "foo.bar",
            },
            [],
        ),
        (
            {
                "HostedZoneName": "bar.",
                "Name": "bar",
            },
            [],
        ),
        (
            {
                "HostedZoneName": "bar.",
                "Name": {"Ref": "pName"},
            },
            [],
        ),
        (
            {
                "HostedZoneName": {"Ref": "pHostedZoneName"},
                "Name": "foo.bar",
            },
            [],
        ),
        (
            {
                "HostedZoneName": "bar",
                "Name": "foo.bar.",
            },
            [
                ValidationError(
                    "'bar' must end in a dot",
                    path=deque(["HostedZoneName"]),
                )
            ],
        ),
        (
            {
                "HostedZoneName": "bar.",
                "Name": "bar.foo.",
            },
            [
                ValidationError(
                    "'bar.foo.' must be a subdomain of or equal to 'bar.'",
                    path=deque(["Name"]),
                )
            ],
        ),
        (
            {
                "HostedZoneName": "bar.",
                "Name": "foobar.",
            },
            [
                ValidationError(
                    "'foobar.' must be a subdomain of or equal to 'bar.'",
                    path=deque(["Name"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
