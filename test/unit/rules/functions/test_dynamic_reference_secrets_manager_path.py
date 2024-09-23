"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.DynamicReferenceSecretsManagerPath import (
    DynamicReferenceSecretsManagerPath,
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReferenceSecretsManagerPath()
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
    "name,instance,path,expected",
    [
        (
            "Valid secrets manager",
            "{{resolve:secretsmanager:Parameter}}",
            ["Resources", "MyResource", "Properties", "LoginProfile", "Password"],
            [],
        ),
        (
            "Valid secrets manager",
            "{{resolve:secretsmanager:Parameter}}",
            ["Parameters", "MyParameter", "Default"],
            [],
        ),
        (
            "Short list",
            "{{resolve:secretsmanager:Parameter}}",
            ["Parameters", "MyParameter"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:secretsmanager:Parameter}}' "
                        "to secrets manager can only be used in resource properties"
                    ),
                    rule=DynamicReferenceSecretsManagerPath(),
                )
            ],
        ),
        (
            "Invalid SSM secure location",
            "{{resolve:secretsmanager:Parameter}}",
            ["Outputs", "MyOutput", "Value"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:secretsmanager:Parameter}}' "
                        "to secrets manager can only be used in resource properties"
                    ),
                    rule=DynamicReferenceSecretsManagerPath(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, context, cfn):
    context = context.evolve(
        path=Path(path),
    )
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {"type": "string"}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
