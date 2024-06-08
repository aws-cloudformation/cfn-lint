"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.certificatemanager.DomainValidationOptions import (
    DomainValidationOptions,
)


@pytest.fixture(scope="module")
def rule():
    rule = DomainValidationOptions()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "DomainName": "foo.bar",
                "ValidationDomain": "bar",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "DomainName": "foo.bar",
                "ValidationDomain": "foo.bar",
            },
            [],
        ),
        (
            {
                "DomainName": "foo.bar",
                "ValidationDomain": {"Ref": "pValidationDomain"},
            },
            [],
        ),
        (
            {
                "DomainName": {"Ref": "pDomainName"},
                "ValidationDomain": "bar",
            },
            [],
        ),
        (
            {
                "DomainName": "foobar",
                "ValidationDomain": "bar",
            },
            [
                ValidationError(
                    "'bar' must be a superdomain of 'foobar'",
                    path=deque(["DomainName"]),
                )
            ],
        ),
        (
            {
                "DomainName": "foo.foo",
                "ValidationDomain": "bar",
            },
            [
                ValidationError(
                    "'bar' must be a superdomain of 'foo.foo'",
                    path=deque(["DomainName"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
