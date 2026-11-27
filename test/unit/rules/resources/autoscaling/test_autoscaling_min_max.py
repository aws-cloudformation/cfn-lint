"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.helpers import get_value_from_path
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


def test_duplicate_branch_values_keep_both_condition_statuses(rule):
    """Same value in both Fn::If branches must not drop a combination.

    MinSize is "1" or "10" and MaxSize is "2" either way, so the
    C=false pair (Min 10, Max 2) violates E3706. Deduping gathered
    values by value alone kept only the C=true MaxSize candidate and
    skipped that pair as conflicting (#4869).
    """
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Parameters": {
            "Mode": {
                "Type": "String",
                "Default": "a",
                "AllowedValues": ["a", "b"],
            },
        },
        "Conditions": {
            "C": {"Fn::Equals": [{"Ref": "Mode"}, "a"]},
        },
        "Resources": {
            "ASG": {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
                "Properties": {
                    "MinSize": {"Fn::If": ["C", "1", "10"]},
                    "MaxSize": {"Fn::If": ["C", "2", "2"]},
                    "AvailabilityZones": ["us-east-1a"],
                },
            },
        },
    }
    cfn = Template("", template, regions=["us-east-1"])
    context = create_context_for_template(cfn)
    validator = CfnTemplateValidator(context=context, cfn=cfn)

    errs = []
    for instance, instance_validator in get_value_from_path(
        validator, template, deque(["Resources", "ASG", "Properties"])
    ):
        errs.extend(rule.validate(instance_validator, "", instance, {}))

    assert [e.message for e in errs] == ["'2' is less than the minimum of 10"]
