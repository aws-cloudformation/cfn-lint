"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.route53.RecordSetAlias import RecordSetAlias


@pytest.fixture(scope="module")
def rule():
    rule = RecordSetAlias()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "AliasTarget": [],
                "TTL": 10,
            },
            [],
        ),
        (
            {
                "TTL": 10,
            },
            [],
        ),
        (
            {
                "AliasTarget": ["Foo"],
                "TTL": 10,
            },
            [
                ValidationError(
                    "Additional properties are not allowed ('TTL' was unexpected)",
                    rule=RecordSetAlias(),
                    path=deque(["TTL"]),
                    validator=None,
                    schema_path=deque(
                        [
                            "then",
                            "properties",
                            "TTL",
                        ]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
