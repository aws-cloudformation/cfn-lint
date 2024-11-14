"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.parameters.Configuration import Configuration
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {},
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Empty is okay",
            {},
            [],
        ),
        (
            "wrong type",
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "String type with Parameter",
            {
                "MyString": {
                    "Type": "String",
                    "AllowedPattern": "1",
                }
            },
            [],
        ),
        (
            "Number type with MinValue",
            {
                "MyNumber": {
                    "Type": "Number",
                    "MinValue": "1",
                }
            },
            [],
        ),
        (
            "AWS type allowed allowed pattern",
            {
                "AWS": {
                    "Type": "AWS::EC2::Image::Id",
                    "AllowedPattern": "^ami-[0-9a-f]+$",
                }
            },
            [],
        ),
        (
            "Number type with AllowedPattern",
            {
                "MyNumber": {
                    "Type": "Number",
                    "AllowedPattern": "1",
                }
            },
            [
                ValidationError(
                    (
                        "'AllowedPattern' is not one of ['AllowedValues', "
                        "'ConstraintDescription', 'Default', 'Description', "
                        "'MaxValue', 'MinValue', 'NoEcho', 'Type']"
                    ),
                    validator="enum",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "then",
                            "propertyNames",
                            "enum",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(["MyNumber", "AllowedPattern"]),
                )
            ],
        ),
        (
            "String type with MinValue",
            {
                "MyString": {
                    "Type": "String",
                    "MinValue": "1",
                }
            },
            [
                ValidationError(
                    (
                        "'MinValue' is not one of ['AllowedPattern', "
                        "'AllowedValues', 'ConstraintDescription', "
                        "'Default', 'Description', 'MaxLength', "
                        "'MinLength', 'NoEcho', 'Type']"
                    ),
                    validator="enum",
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "else",
                            "then",
                            "propertyNames",
                            "enum",
                        ]
                    ),
                    rule=Configuration(),
                    path=deque(["MyString", "MinValue"]),
                )
            ],
        ),
        (
            "Bad Name",
            {
                "Ref&3": {
                    "Type": "String",
                }
            },
            [
                ValidationError(
                    "'Ref&3' does not match any of the regexes: '^[a-zA-Z0-9]+$'",
                    validator="additionalProperties",
                    schema_path=deque(["additionalProperties"]),
                    rule=Configuration(),
                    path=deque(["Ref&3"]),
                )
            ],
        ),
        (
            "Long key name",
            {
                "a"
                * 256: {
                    "Type": "String",
                }
            },
            [
                ValidationError(
                    "expected maximum length: 255, found: 256",
                    validator="maxLength",
                    schema_path=deque(["propertyNames", "maxLength"]),
                    rule=None,  # none becuase we don't load child rule
                    path=deque(["a" * 256]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
