"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import ContextManager
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.AvailabilityZone import (
    AvailabilityZone,  # pylint: disable=E0401
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = AvailabilityZone()
    yield rule


@pytest.fixture(scope="module")
def validator():
    cfn = Template(
        "",
        {
            "Resources": {
                "MySqs": {
                    "Type": "AWS::SQS::Queue",
                }
            }
        },
    )
    context_manager = ContextManager(cfn)
    context = context_manager.create_context_for_template(["us-east-1"]).evolve(
        functions=FUNCTIONS
    )
    context.path = deque(["Resources", "MySqs", "Properties"])
    yield CfnTemplateValidator(schema={}, context=context, cfn=cfn)


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid ref",
            {"Ref": "AZ"},
            None,
            [],
        ),
        (
            "Valid list ref",
            [{"Ref": "AZ"}],
            None,
            [],
        ),
        (
            "Valid inside Ref",
            "us-east-1a",
            "Ref",
            [],
        ),
        (
            "Valid GetAZs",
            ["us-east-1a", "us-east-1b"],
            "Fn::GetAZs",
            [],
        ),
        (
            "Invalid type",
            True,
            deque(["Resources", "MySqs", "Properties"]),
            [],
        ),
        (
            "Invalid hardcoded string",
            "us-east-1a",
            deque(["Resources", "MySqs", "Properties"]),
            [
                ValidationError(
                    ("Avoid hardcoding availability zones 'us-east-1a'"),
                    rule=AvailabilityZone(),
                )
            ],
        ),
        (
            "Invalid hardcoded array",
            ["us-east-1a", "us-east-1b"],
            deque(["Resources", "MySqs", "Properties"]),
            [
                ValidationError(
                    ("Avoid hardcoding availability zones 'us-east-1a'"),
                    rule=AvailabilityZone(),
                ),
                ValidationError(
                    ("Avoid hardcoding availability zones 'us-east-1b'"),
                    rule=AvailabilityZone(),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=path,
        )
    )
    errors = list(rule.validate(validator, False, instance, {}))
    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert errors == expected, f"Test {name!r} got {errors!r}"
