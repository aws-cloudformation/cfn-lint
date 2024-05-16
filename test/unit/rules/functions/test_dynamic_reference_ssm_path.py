"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.DynamicReferenceSsmPath import DynamicReferenceSsmPath
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReferenceSsmPath()
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
            "Valid SSM Parameter",
            "{{resolve:ssm:Parameter}}",
            ["Resources", "MyResource", "Properties", "LoginProfile", "Password"],
            [],
        ),
        (
            "Valid SSM Parameter in outputs",
            "{{resolve:ssm:Parameter}}",
            ["Outputs", "MyOutput", "Value"],
            [],
        ),
        (
            "Valid SSM Parameter in parameters",
            "{{resolve:ssm:Parameter}}",
            ["Parameters", "MyParameter", "Default"],
            [],
        ),
        (
            "Invalid SSM secure location",
            "{{resolve:ssm:Parameter}}",
            ["Outputs", "MyOutput", "Export", "Name"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM secure location in Outputs",
            "{{resolve:ssm:Parameter}}",
            ["Outputs"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM parameter type in parameters",
            "{{resolve:ssm:Parameter}}",
            ["Parameters", "MyParameter", "Type"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM parameter type in parameters 2",
            "{{resolve:ssm:Parameter}}",
            ["Parameters", "MyParameter"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM parameter in Resources",
            "{{resolve:ssm:Parameter}}",
            ["Resources", "MyResource"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM parameter in Resource Type",
            "{{resolve:ssm:Parameter}}",
            ["Resources", "MyResource", "Type"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM parameter in Metadata",
            "{{resolve:ssm:Parameter}}",
            ["Metadata"],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
        (
            "Invalid SSM parameter in no location",
            "{{resolve:ssm:Parameter}}",
            [],
            [
                ValidationError(
                    (
                        "Dynamic reference '{{resolve:ssm:Parameter}}' "
                        "to SSM parameters are not allowed here"
                    ),
                    rule=DynamicReferenceSsmPath(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, context, cfn):
    context = context.evolve(path=Path(path=path))
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {"type": "string"}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
