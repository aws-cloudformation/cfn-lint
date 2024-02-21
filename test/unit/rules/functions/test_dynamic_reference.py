"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.DynamicReference import DynamicReference
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReference()
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
    "name,instance,schema,expected",
    [
        (
            "Valid SSM Parameter",
            "{{resolve:ssm:Parameter}}",
            {"type": "test"},
            [],
        ),
        (
            "Valid SSM Parameter with integer",
            "{{resolve:ssm:Parameter:1}}",
            {"type": "test"},
            [],
        ),
        (
            "Valid when item isn't a string",
            {},
            {"type": "test"},
            [],
        ),
        (
            "Basic error when wrong length",
            "{{resolve:ssm}}",
            {"type": "test"},
            [
                ValidationError(
                    "['resolve', 'ssm'] is too short (3)",
                    validator="minItems",
                    rule=DynamicReference(),
                )
            ],
        ),
        (
            "Invalid SSM Parameter with string version",
            "{{resolve:ssm:Parameter:a}}",
            {"type": "test"},
            [
                ValidationError(
                    "'a' does not match '\\\\d+'",
                    validator="pattern",
                    rule=DynamicReference(),
                )
            ],
        ),
        (
            "Valid secret manager",
            "{{resolve:secretsmanager:Secret}}",
            {"type": "test"},
            [],
        ),
        (
            "Valid secret manager with secretstring",
            "{{resolve:secretsmanager:Secret:SecretString}}",
            {"type": "test"},
            [],
        ),
        (
            "Valid secret manager from another account",
            "{{resolve:secretsmanager:arn:aws:secretsmanager:us-west-2:123456789012:secret:MySecret-a1b2c3:SecretString:password}}",
            {"type": "test"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.dynamicReference(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
