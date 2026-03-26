"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.autoscaling.AutoScalingMinMaxSize import (
    AutoScalingMinMaxSize,
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    yield AutoScalingMinMaxSize()


@pytest.fixture(scope="module")
def cfn():
    return Template("", {}, regions=["us-east-1"])


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid - MaxSize > MinSize",
            {"MinSize": "1", "MaxSize": "10"},
            [],
        ),
        (
            "Valid - MaxSize == MinSize",
            {"MinSize": "5", "MaxSize": "5"},
            [],
        ),
        (
            "Invalid - MaxSize < MinSize",
            {"MinSize": "5", "MaxSize": "2"},
            [
                ValidationError(
                    "'2' is less than the minimum of 5",
                    path=deque(["MaxSize"]),
                    rule=AutoScalingMinMaxSize(),
                    validator="minimum",
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "this",
                            "properties",
                            "MaxSize",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        (
            "Valid - non-numeric values skipped",
            {"MinSize": {"Ref": "Param"}, "MaxSize": "10"},
            [],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
