"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.DynamicReference import DynamicReference
from cfnlint.template import Template


class _TestRule:
    def validate(self, validator, s, instance, schema):
        return
        yield


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
    "name,instance,schema,child_rules,expected",
    [
        (
            "Valid SSM Parameter",
            "{{resolve:ssm:Parameter}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Valid SSM Parameter with no rules",
            "{{resolve:ssm:Parameter}}",
            {"type": "test"},
            {
                "E1051": None,
                "E1027": None,
            },
            [],
        ),
        (
            "Valid SSM secure Parameter",
            "{{resolve:ssm-secure:Parameter}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Valid SSM secure string with no rules",
            "{{resolve:ssm-secure:Parameter}}",
            {"type": "test"},
            {
                "E1051": None,
                "E1027": None,
            },
            [],
        ),
        (
            "Valid SSM Parameter with integer",
            "{{resolve:ssm:Parameter:1}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Valid when item isn't a string",
            {},
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Basic error when wrong length",
            "{{resolve:ssm}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
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
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
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
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Valid secret manager with no child rules",
            "{{resolve:secretsmanager:Secret}}",
            {"type": "test"},
            {
                "E1051": None,
                "E1027": None,
            },
            [],
        ),
        (
            "Valid secret manager with secretstring",
            "{{resolve:secretsmanager:Secret:SecretString}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Valid secret manager from another account",
            "{{resolve:secretsmanager:arn:aws:secretsmanager:us-west-2:123456789012:secret:MySecret-a1b2c3:SecretString:password}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [],
        ),
        (
            "Invalid SSM Parameter with string version",
            "{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:012345678901:secret:my-secret:SecretString::::}}",
            {"type": "test"},
            {
                "E1051": _TestRule(),
                "E1027": _TestRule(),
            },
            [
                ValidationError(
                    "['resolve', 'secretsmanager', 'arn', 'aws', "
                    "'secretsmanager', 'us-east-1', '012345678901', "
                    "'secret', 'my-secret', 'SecretString', "
                    "'', '', '', ''] is too long (13)",
                    validator="maxItems",
                    rule=DynamicReference(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, child_rules, expected, rule, context, cfn):
    rule.child_rules = child_rules
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.dynamicReference(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
