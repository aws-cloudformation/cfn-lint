"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest
import yaml

from cfnlint.decode.mark import Mark
from cfnlint.decode.node import dict_node, str_node
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
                    "'arn:aws-us-gov:iam::123456789012:role/test' is not "
                    "of type 'object'",
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


def test_validate_string_content_as_str_node(rule, validator):
    # Content decoded from a template arrives as a str_node, not a plain
    # str. Regression test for #4894: a well-formed JSON string must not
    # draw the generic parser error, and a malformed one must report the
    # actual parse defect instead of that same generic message.
    valid = str_node(
        '{"schemaVersion":"2.2","description":"ok","mainSteps":[]}',
        Mark(0, 0),
        Mark(0, 0),
    )
    assert list(rule.validate(validator, {}, valid, {})) == []

    malformed = str_node(
        "{bad json",
        Mark(0, 0),
        Mark(0, 0),
    )
    errs = list(rule.validate(validator, {}, malformed, {}))
    assert len(errs) == 1
    assert errs[0].message.startswith("Document is not valid (")
    assert "a string or stream input is required" not in errs[0].message

    # Inner schema validation must also run on string content: an empty
    # schemaVersion parses as null and fails the enum check.
    bad_version = str_node(
        '{"schemaVersion":}',
        Mark(0, 0),
        Mark(0, 0),
    )
    errs = list(rule.validate(validator, {}, bad_version, {}))
    assert any("is not one of" in err.message for err in errs)
    assert any("2.2" in err.message for err in errs)
    assert not any(
        "a string or stream input is required" in err.message for err in errs
    )


def test_validate_object_content_as_dict_node(rule, validator):
    # Object-form Content is untouched by the string fix.
    valid = dict_node(
        {
            "schemaVersion": "2.2",
            "mainSteps": [{"action": "aws:runShellScript"}],
        },
        Mark(0, 0),
        Mark(0, 0),
    )
    assert list(rule.validate(validator, {}, valid, {})) == []


def test_validate_by_py_version(rule, validator):
    document = '{ "arn:aws-us-gov:iam::123456789012:role/test"'

    # Error wording depends on PyYAML's loader (C libyaml vs pure-Python),
    # not the Python version or platform.
    if not yaml.__with_libyaml__:
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
