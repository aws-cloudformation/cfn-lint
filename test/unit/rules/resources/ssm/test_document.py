"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import sys
from collections import deque

import pytest

from cfnlint.jsonschema.validators import ValidationError
from cfnlint.rules.resources.ssm.Document import Document


@pytest.fixture(scope="module")
def rule():
    rule = Document()
    yield rule


@pytest.mark.parametrize(
    "name,document,expected",
    [
        (
            "Valid string yaml",
            """
            schemaVersion: "2.2"
            mainSteps:
                - action: aws:runShellScript
            """,
            [],
        ),
        (
            "Valid string json",
            """
            {
                "schemaVersion": "2.2",
                "mainSteps": [
                    {
                        "action": "aws:runShellScript"
                    }
                ]
            }
            """,
            [],
        ),
        (
            "Valid object",
            {
                "schemaVersion": "2.2",
                "mainSteps": [
                    {"action": "aws:runShellScript"},
                ],
            },
            [],
        ),
        (
            "InValid string yaml",
            """
            schemaVersion: 2.2
            mainSteps:
                - action: aws:runShellScript
            """,
            [
                ValidationError(
                    "2.2 is not of type 'string'",
                    rule=Document(),
                    validator="type",
                    schema_path=deque(["properties", "schemaVersion", "type"]),
                    path=deque(["schemaVersion"]),
                )
            ],
        ),
        (
            "The wrong type but string",
            "arn:aws-us-gov:iam::123456789012:role/test",
            [
                ValidationError(
                    (
                        "'arn:aws-us-gov:iam::123456789012:role/test' is not "
                        "of type 'object'"
                    ),
                    rule=Document(),
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque([]),
                )
            ],
        ),
        (
            "Invalid schema version in object",
            {
                "schemaVersion": 2.2,
                "mainSteps": [
                    {"action": "aws:runShellScript"},
                ],
            },
            [
                ValidationError(
                    "2.2 is not of type 'string'",
                    rule=Document(),
                    validator="type",
                    schema_path=deque(["properties", "schemaVersion", "type"]),
                    path=deque(["schemaVersion"]),
                )
            ],
        ),
        (
            "Invalid type",
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    rule=Document(),
                    validator="type",
                    schema_path=deque(["type"]),
                    path=deque([]),
                )
            ],
        ),
    ],
)
def test_validate(
    name,
    document,
    expected,
    rule,
    validator,
):
    errs = list(rule.validate(validator, {}, document, {}))

    assert errs == expected, f"Test {name!r} failed with {errs!r}"


def test_validate_by_py_version(rule, validator):
    document = '{ "arn:aws-us-gov:iam::123456789012:role/test"'

    if sys.version_info < (3, 9) and sys.platform == "darwin":
        message = (
            "Document is not valid (\"expected ',' or '}', but got '<stream end>'\")"
        )
    else:
        message = "Document is not valid (\"did not find expected ',' or '}'\")"

    expected = [
        ValidationError(
            message,
            rule=Document(),
            validator="type",
            schema_path=deque([]),
            path=deque([]),
        )
    ]

    errs = list(rule.validate(validator, {}, document, {}))

    assert errs == expected
