"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.DynamicReferenceSpaces import DynamicReferenceSpaces
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReferenceSpaces()
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
            "Invalid - space before resolve for ssm",
            "{{ resolve:ssm:SomeParameter }}",
            [
                ValidationError(
                    (
                        "'{{ resolve:ssm:SomeParameter }}' has spaces and will"
                        " not be resolved as a dynamic reference. Remove spaces"
                        " from '{{resolve:...}}'"
                    ),
                    rule=DynamicReferenceSpaces(),
                ),
            ],
        ),
        (
            "Invalid - space before resolve for ssm-secure",
            "{{ resolve:ssm-secure:SomeParameter }}",
            [
                ValidationError(
                    (
                        "'{{ resolve:ssm-secure:SomeParameter }}' has spaces"
                        " and will not be resolved as a dynamic reference."
                        " Remove spaces from '{{resolve:...}}'"
                    ),
                    rule=DynamicReferenceSpaces(),
                ),
            ],
        ),
        (
            "Invalid - space before resolve for secretsmanager",
            "{{ resolve:secretsmanager:SomeSecret }}",
            [
                ValidationError(
                    (
                        "'{{ resolve:secretsmanager:SomeSecret }}' has spaces"
                        " and will not be resolved as a dynamic reference."
                        " Remove spaces from '{{resolve:...}}'"
                    ),
                    rule=DynamicReferenceSpaces(),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.dynamicReferenceSpaces(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
