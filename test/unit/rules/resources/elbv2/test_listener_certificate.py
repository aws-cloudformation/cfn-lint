"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.elasticloadbalancingv2.ListenerCertificate import (
    ListenerCertificate,
)


@pytest.fixture(scope="module")
def rule():
    rule = ListenerCertificate()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Protocol": "HTTP"},
            [],
        ),
        (
            {"Protocol": "HTTPS", "Certificates": ["Certificate"]},
            [],
        ),
        (
            {
                "Protocol": "TLS",
            },
            [
                ValidationError(
                    ("'Certificates' is a required property"),
                    rule=ListenerCertificate(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
