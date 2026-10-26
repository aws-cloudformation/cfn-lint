"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest
import yaml

from cfnlint.context import Path
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
                    path=deque(["Content", "schemaVersion"]),
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
                    path=deque(["Content"]),
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
                    path=deque(["Content", "schemaVersion"]),
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
                    path=deque(["Content"]),
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
    # The rule is keyworded at Properties, so the instance is the
    # Properties object and Content is one of its keys.
    properties = {"DocumentType": "Automation", "Content": document}
    errs = list(rule.validate(validator, {}, properties, {}))

    assert errs == expected


@pytest.mark.parametrize(
    "template",
    [
        {
            "Parameters": {
                "DocTypeParam": {"Type": "String", "Default": "Automation"},
            },
            "Resources": {
                "ConfigSchema": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "ApplicationConfigurationSchema",
                        "DocumentFormat": "JSON",
                        "Content": {
                            "$schema": "http://json-schema.org/draft-04/schema#",
                            "type": "object",
                        },
                    },
                },
                "ConfigData": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "ApplicationConfiguration",
                        "DocumentFormat": "JSON",
                        "Content": {"featureEnabled": True},
                    },
                },
                "AutomationDoc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "Automation",
                        "DocumentFormat": "YAML",
                        "Content": {"description": "no schemaVersion"},
                    },
                },
                "IntrinsicTypeDoc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": {"Ref": "DocTypeParam"},
                        "DocumentFormat": "YAML",
                        "Content": {"description": "no schemaVersion"},
                    },
                },
            },
        }
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "resource_name,expected_count",
    [
        ("ConfigSchema", 0),
        ("ConfigData", 0),
        ("AutomationDoc", 1),
        ("IntrinsicTypeDoc", 1),
    ],
)
def test_validate_document_type_scoping(
    resource_name,
    expected_count,
    rule,
    validator,
):
    """E3051 skips AppConfig document types but still validates the rest"""
    properties = validator.cfn.template["Resources"][resource_name]["Properties"]
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(path=deque(["Resources", resource_name, "Properties"]))
        )
    )
    errs = list(rule.validate(validator, {}, properties, {}))

    assert len(errs) == expected_count, f"{resource_name} got {errs!r}"


@pytest.mark.parametrize(
    "document_type",
    [
        "ApplicationConfiguration",
        "ApplicationConfigurationSchema",
    ],
)
def test_validate_appconfig_string_content(document_type, rule, validator):
    """E3051 skips string Content on AppConfig types before decoding it"""
    properties = {
        "DocumentType": document_type,
        "Content": "featureEnabled: true",
    }
    errs = list(rule.validate(validator, {}, properties, {}))

    assert errs == []


def test_validate_command_without_schema_version(rule, validator):
    """A Command document without schemaVersion is still flagged,
    proving the AppConfig exemption is narrow rather than broad"""
    properties = {
        "DocumentType": "Command",
        "Content": {"description": "no schemaVersion"},
    }
    errs = list(rule.validate(validator, {}, properties, {}))

    assert len(errs) == 1
    assert errs[0].message == "'schemaVersion' is a required property"
    assert errs[0].path == deque(["Content"])


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
            path=deque(["Content"]),
        )
    ]

    properties = {"DocumentType": "Automation", "Content": document}
    errs = list(rule.validate(validator, {}, properties, {}))

    assert errs == expected
