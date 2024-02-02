"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import ContextManager
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.RetentionPeriodOnResourceTypesWithAutoExpiringContent import (  # noqa: E501
    RetentionPeriodOnResourceTypesWithAutoExpiringContent,
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = RetentionPeriodOnResourceTypesWithAutoExpiringContent()
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
    "name,instance,expected",
    [
        (
            "Valid version",
            {"MessageRetentionPeriod": "90"},
            [],
        ),
        (
            "Invalid type ",
            [],
            [],
        ),
        (
            "Invalid when not specified",
            {},
            [
                ValidationError(
                    (
                        "The default retention period will delete the data after "
                        "a pre-defined time. Set an explicit values to avoid data "
                        "loss on resource. 'MessageRetentionPeriod' is a "
                        "required property"
                    ),
                    rule=RetentionPeriodOnResourceTypesWithAutoExpiringContent(),
                    schema_path=deque(["required"]),
                    validator="required",
                    validator_value=["MessageRetentionPeriod"],
                    instance={},
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert errors == expected, f"Test {name!r} got {errors!r}"
