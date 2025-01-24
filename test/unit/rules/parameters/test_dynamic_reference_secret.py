"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.parameters.DynamicReferenceSecret import DynamicReferenceSecret
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = DynamicReferenceSecret()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {
            "Parameters": {
                "MyParameter": {
                    "Type": "String",
                }
            },
            "Resources": {},
        },
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "REFing a parameter without a string",
            [],
            deque([]),
            [],
        ),
        (
            "REFing a resource=",
            "MyResource",
            deque([]),
            [],
        ),
        (
            "REFing a parameter",
            "MyParameter",
            deque([]),
            [
                ValidationError(
                    "Use dynamic references over parameters for secrets",
                    rule=DynamicReferenceSecret(),
                )
            ],
        ),
        (
            "REFing a parameter in a sub",
            "MyParameter",
            deque(["Fn::Sub"]),
            [],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context.evolve(path=Path(path)), cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
