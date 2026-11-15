"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from copy import deepcopy

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
        (
            "Valid - DesiredCapacity between MinSize and MaxSize",
            {"MinSize": "1", "MaxSize": "10", "DesiredCapacity": "5"},
            [],
        ),
        (
            "Valid - DesiredCapacity equal to MinSize and MaxSize",
            {"MinSize": "2", "MaxSize": "2", "DesiredCapacity": "2"},
            [],
        ),
        (
            "Invalid - DesiredCapacity > MaxSize",
            {"MinSize": "1", "MaxSize": "2", "DesiredCapacity": "3"},
            [
                ValidationError(
                    "'3' is greater than the maximum of 2",
                    path=deque(["DesiredCapacity"]),
                    rule=AutoScalingMinMaxSize(),
                    validator="maximum",
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "this",
                            "properties",
                            "DesiredCapacity",
                            "maximum",
                        ]
                    ),
                ),
            ],
        ),
        (
            "Invalid - DesiredCapacity < MinSize",
            {"MinSize": "2", "MaxSize": "4", "DesiredCapacity": "1"},
            [
                ValidationError(
                    "'1' is less than the minimum of 2",
                    path=deque(["DesiredCapacity"]),
                    rule=AutoScalingMinMaxSize(),
                    validator="minimum",
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "this",
                            "properties",
                            "DesiredCapacity",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        (
            "Invalid - MaxSize < MinSize and DesiredCapacity > MaxSize",
            {"MinSize": "3", "MaxSize": "2", "DesiredCapacity": "5"},
            [
                ValidationError(
                    "'5' is greater than the maximum of 2",
                    path=deque(["DesiredCapacity"]),
                    rule=AutoScalingMinMaxSize(),
                    validator="maximum",
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "this",
                            "properties",
                            "DesiredCapacity",
                            "maximum",
                        ]
                    ),
                ),
                ValidationError(
                    "'2' is less than the minimum of 3",
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
            "Valid - non-numeric DesiredCapacity skipped",
            {"MinSize": "1", "MaxSize": "2", "DesiredCapacity": {"Ref": "Param"}},
            [],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"


_conditions_template = {
    "Parameters": {
        "Env": {"Type": "String", "AllowedValues": ["dev", "prod"]},
    },
    "Conditions": {
        "IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
        "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
    },
    "Resources": {},
}


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid - DesiredCapacity and MinSize use Fn::If on exclusive conditions",
            {
                "MinSize": {"Fn::If": ["IsProd", "2", "1"]},
                "MaxSize": "4",
                "DesiredCapacity": {"Fn::If": ["IsDev", "1", "3"]},
            },
            [],
        ),
        (
            "Valid - DesiredCapacity and MaxSize use Fn::If on exclusive conditions",
            {
                "MinSize": "1",
                "MaxSize": {"Fn::If": ["IsDev", "2", "6"]},
                "DesiredCapacity": {"Fn::If": ["IsProd", "5", "2"]},
            },
            [],
        ),
        (
            "Invalid - Fn::If DesiredCapacity above a literal MaxSize",
            {
                "MinSize": "1",
                "MaxSize": "2",
                "DesiredCapacity": {"Fn::If": ["IsProd", "5", "1"]},
            },
            ["'5' is greater than the maximum of 2"],
        ),
    ],
)
def test_validate_conditions(name, instance, expected, rule):
    template = deepcopy(_conditions_template)
    template["Resources"]["Group"] = {
        "Type": "AWS::AutoScaling::AutoScalingGroup",
        "Properties": instance,
    }
    cfn = Template("", template, regions=["us-east-1"])
    validator = CfnTemplateValidator(context=create_context_for_template(cfn), cfn=cfn)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert [err.message for err in errs] == expected, f"Test {name!r} got {errs!r}"
