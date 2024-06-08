"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError

# ruff: noqa: E501
from cfnlint.rules.resources.UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes import (
    UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes,
)


@pytest.fixture(scope="module")
def rule():
    rule = UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Type": "AWS::EC2::VPC",
            },
            [],
        ),
        (
            {
                "Type": ["AWS::EC2::VPC"],
            },
            [],
        ),
        (
            {
                "Type": "AWS::SQS::Queue",
                "DeletionPolicy": "Foo",
                "UpdateReplacePolicy": "Foo",
            },
            [],
        ),
        (
            {
                "Type": "AWS::SQS::Queue",
            },
            [
                ValidationError(
                    (
                        "'DeletionPolicy' is a required property (The default "
                        "action when replacing/removing a resource is to delete "
                        "it. Set explicit values for stateful resource)"
                    ),
                    rule=UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["required"]),
                ),
                ValidationError(
                    (
                        "'UpdateReplacePolicy' is a required property (The default "
                        "action when replacing/removing a resource is to delete "
                        "it. Set explicit values for stateful resource)"
                    ),
                    rule=UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["required"]),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
