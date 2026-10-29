"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from collections import deque

import pytest
import yaml

from cfnlint.api import lint
from cfnlint.context import Path
from cfnlint.jsonschema.validators import ValidationError
from cfnlint.rules.resources.ssm.Document import Document


@pytest.fixture(scope="module")
def rule():
    rule = Document()
    yield rule


def _at_content(validator, resource_name="Doc"):
    return validator.evolve(
        context=validator.context.evolve(
            path=Path(
                path=deque(["Resources", resource_name, "Properties", "Content"]),
            )
        )
    )


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
    errs = list(rule.validate(_at_content(validator), {}, document, {}))

    assert errs == expected, f"Test {name!r} failed with {errs!r}"


@pytest.mark.parametrize(
    "template",
    [
        {
            "Parameters": {
                "DocTypeParam": {"Type": "String", "Default": "Automation"},
                "Env": {"Type": "String", "Default": "prod"},
            },
            "Conditions": {"IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
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
                "NoDocumentType": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
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
                "ConditionalAppConfigDoc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": {
                            "Fn::If": [
                                "IsProd",
                                "ApplicationConfiguration",
                                "ApplicationConfigurationSchema",
                            ]
                        },
                        "Content": {"featureEnabled": True},
                    },
                },
                "ConditionalPlainDoc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": {"Fn::If": ["IsProd", "Command", "Automation"]},
                        "Content": {"description": "no schemaVersion"},
                    },
                },
                "ConditionalMixedDoc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": {
                            "Fn::If": ["IsProd", "ApplicationConfiguration", "Command"]
                        },
                        "Content": {"featureEnabled": True},
                    },
                },
                "ConfigDataString": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "ApplicationConfiguration",
                        "Content": "featureEnabled: true",
                    },
                },
                "ConfigSchemaString": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "ApplicationConfigurationSchema",
                        "Content": '{"type": "object"}',
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
        ("NoDocumentType", 1),
        ("IntrinsicTypeDoc", 1),
        ("ConditionalAppConfigDoc", 0),
        ("ConditionalPlainDoc", 1),
        ("ConditionalMixedDoc", 0),
        ("ConfigDataString", 0),
        ("ConfigSchemaString", 0),
    ],
)
def test_validate_document_type_scoping(
    resource_name,
    expected_count,
    rule,
    validator,
):
    """E3051 skips AppConfig document types but still validates the rest"""
    content = validator.cfn.template["Resources"][resource_name]["Properties"][
        "Content"
    ]
    errs = list(rule.validate(_at_content(validator, resource_name), {}, content, {}))

    assert len(errs) == expected_count, f"{resource_name} got {errs!r}"


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

    errs = list(rule.validate(_at_content(validator), {}, document, {}))

    assert errs == expected


@pytest.mark.parametrize(
    "name,resources,expected",
    [
        (
            "Content from a Ref is not resolvable",
            {
                "Doc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "Command",
                        "Content": {"Ref": "DocBody"},
                    },
                }
            },
            [],
        ),
        (
            "Content from a GetAtt is not resolvable",
            {
                "Stack1": {
                    "Type": "AWS::CloudFormation::Stack",
                    "Properties": {"TemplateURL": "https://example.com/t.yaml"},
                },
                "Doc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "Command",
                        "Content": {"Fn::GetAtt": ["Stack1", "Outputs.Body"]},
                    },
                },
            },
            [],
        ),
        (
            "Content from a Sub is not resolvable",
            {
                "Doc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "Command",
                        "Content": {"Fn::Sub": '{"schemaVersion":"${DocBody}"}'},
                    },
                }
            },
            [],
        ),
        (
            "Content from a Fn::If validates each branch",
            {
                "Doc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "Command",
                        "Content": {
                            "Fn::If": [
                                "IsProd",
                                {"schemaVersion": "2.2", "mainSteps": []},
                                {"description": "no schemaVersion"},
                            ]
                        },
                    },
                }
            },
            ["E3051"],
        ),
        (
            "A Command document still needs a schemaVersion",
            {
                "Doc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "Command",
                        "Content": {"description": "no schemaVersion"},
                    },
                }
            },
            ["E3051"],
        ),
        (
            "An AppConfig document does not",
            {
                "Doc": {
                    "Type": "AWS::SSM::Document",
                    "Properties": {
                        "DocumentType": "ApplicationConfiguration",
                        "Content": {"featureEnabled": True},
                    },
                }
            },
            [],
        ),
    ],
)
def test_keyword_registration(name, resources, expected):
    """Content behind an intrinsic function is filtered before E3051 runs"""
    template = {
        "Parameters": {
            "DocBody": {"Type": "String", "Default": '{"schemaVersion":"2.2"}'},
            "Env": {"Type": "String", "Default": "prod"},
        },
        "Conditions": {"IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
        "Resources": resources,
    }
    matches = lint(json.dumps(template), regions=["us-east-1"])

    assert [
        match.rule.id for match in matches if match.rule.id == "E3051"
    ] == expected, f"Test {name!r} failed with {matches!r}"
