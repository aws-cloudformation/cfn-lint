"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.cloudfront.Aliases import Aliases


@pytest.fixture(scope="module")
def rule():
    rule = Aliases()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            "www.example.com",
            [],
        ),
        (
            "example.com",
            [],
        ),
        (
            "email.exa.ple.com",
            [],
        ),
        (
            "mx1.example.eu",
            [],
        ),
        (
            "e-mail.example.amsterdam",
            [],
        ),
        ("xn-caf-dma.com", []),
        ("www.example.eu", []),
        (
            "111.example.com",
            [],
        ),
        (
            "email.internal.example.eu",
            [],
        ),
        (
            "e-mail.internal.ex-ample.eu",
            [],
        ),
        (
            "www.example.google",
            [],
        ),
        (
            "1111111111.ex--ample.nl",
            [],
        ),
        (
            "*.example.com",
            [],
        ),
        (
            {},
            [],
        ),
        (
            "email.*.example.com",
            [
                ValidationError(
                    (
                        "'email.*.example.com' does not match "
                        "'^(?!.*(?:\\\\.\\\\*\\\\.)).*'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "WWW.EXAMPLE.COM",
            [
                ValidationError(
                    (
                        "'WWW.EXAMPLE.COM' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "-example.com",
            [
                ValidationError(
                    (
                        "'-example.com' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "example.c",
            [
                ValidationError(
                    (
                        "'example.c' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "www.example.com ",
            [
                ValidationError(
                    (
                        "'www.example.com ' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "www.-example.com",
            [
                ValidationError(
                    (
                        "'www.-example.com' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "-www.example.com",
            [
                ValidationError(
                    (
                        "'-www.example.com' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
        (
            "www.example.com-",
            [
                ValidationError(
                    (
                        "'www.example.com-' does not match "
                        "'^(?:[a-z0-9\\\\*](?:[a-z0-9-]{0,61}[a-z0-9])?\\\\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$'"
                    ),
                    rule=Aliases(),
                    path=deque([]),
                    validator="pattern",
                    schema_path=deque(["pattern"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
