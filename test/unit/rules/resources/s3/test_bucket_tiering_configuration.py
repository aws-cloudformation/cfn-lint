"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.s3.BucketTieringConfiguration import (
    BucketTieringConfiguration,
)


@pytest.fixture(scope="module")
def rule():
    rule = BucketTieringConfiguration()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {},
            [],
        ),
        (
            {"AccessTier": "ARCHIVE_ACCESS"},
            [],
        ),
        (
            {
                "AccessTier": "ARCHIVE_ACCESS",
                "Days": "90",
            },
            [],
        ),
        (
            {
                "AccessTier": "ARCHIVE_ACCESS",
                "Days": "a",
            },
            [],
        ),
        (
            {
                "AccessTier": "ARCHIVE_ACCESS",
                "Days": 1,
            },
            [
                ValidationError(
                    ("1 is less than the minimum of 90"),
                    path=deque(["Days"]),
                    validator="minimum",
                    schema_path=deque(["minimum"]),
                    rule=BucketTieringConfiguration(),
                )
            ],
        ),
        (
            {
                "AccessTier": "ARCHIVE_ACCESS",
                "Days": 99999,
            },
            [
                ValidationError(
                    ("99999 is greater than the maximum of 730"),
                    path=deque(["Days"]),
                    validator="maximum",
                    schema_path=deque(["maximum"]),
                    rule=BucketTieringConfiguration(),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
