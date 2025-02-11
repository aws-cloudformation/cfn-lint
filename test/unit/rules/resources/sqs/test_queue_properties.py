"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.sqs.QueueProperties import QueueProperties


@pytest.fixture(scope="module")
def rule():
    rule = QueueProperties()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "FifoQueue": True,
            },
            [],
        ),
        (
            {
                "FifoQueue": True,
                "QueueName": "test.fifo",
            },
            [],
        ),
        (
            {
                "FifoQueue": True,
                "QueueName": "test",
            },
            [
                ValidationError(
                    "'test' does not match '^.*\\\\.fifo$'",
                    rule=QueueProperties(),
                    path=deque(["QueueName"]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            0,
                            "then",
                            "then",
                            "properties",
                            "QueueName",
                            "pattern",
                        ]
                    ),
                )
            ],
        ),
        (
            {
                "ContentBasedDeduplication": True,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "('ContentBasedDeduplication' was unexpected)"
                    ),
                    rule=QueueProperties(),
                    path=deque(["ContentBasedDeduplication"]),
                    validator=None,
                    schema_path=deque(
                        ["allOf", 1, "then", "properties", "ContentBasedDeduplication"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
