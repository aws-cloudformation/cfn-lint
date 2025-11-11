"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.constants.Configuration import Configuration
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
    "name,instance,expected_error_count",
    [
        ("Empty is okay", {}, 0),
        ("Wrong type", [], 1),
        (
            "Valid constant names",
            {
                "BucketPrefix": "my-bucket",
                "Environment": "prod",
                "Count123": 5,
                "ABC": "value",
            },
            0,
        ),
        ("Invalid constant name with hyphen", {"Invalid-Name": "value"}, 1),
        ("Invalid constant name with dot", {"Invalid.Name": "value"}, 1),
        ("Invalid constant name with space", {"Invalid Name": "value"}, 1),
        ("Constant name too long", {"A" * 256: "value"}, 1),
        (
            "Empty constant name",
            {"": "value"},
            2,
        ),  # Triggers both pattern and minLength errors
    ],
)
def test_configuration(name, instance, expected_error_count, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))

    assert len(errs) == expected_error_count, (
        f"Test {name!r} expected {expected_error_count} errors, got {len(errs)}: {errs}"
    )
