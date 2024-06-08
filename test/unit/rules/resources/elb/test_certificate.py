"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.elb.Certificate import Certificate


@pytest.fixture(scope="module")
def rule():
    rule = Certificate()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Protocol": "HTTP"},
            [],
        ),
        (
            {"Protocol": "HTTPS", "SSLCertificateId": "Id"},
            [],
        ),
        (
            {
                "Protocol": "SSL",
            },
            [
                ValidationError(
                    ("'SSLCertificateId' is a required property"),
                    rule=Certificate(),
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
