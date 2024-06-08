"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.BothUpdateReplacePolicyDeletionPolicyNeeded import (
    UpdateReplacePolicyDeletionPolicy,
)


@pytest.fixture(scope="module")
def rule():
    rule = UpdateReplacePolicyDeletionPolicy()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyResource": {
                "Type": "AWS::S3::Bucket",
            }
        }
    }


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid with nothing specified",
            {},
            deque(["Resources", "MyResource"]),
            [],
        ),
        (
            "Valid both update and replacy policy",
            {
                "Type": "AWS::S3::Bucket",
                "DeletionPolicy": "Retain",
                "UpdateReplacePolicy": "Retain",
            },
            deque(["Resources", "MyResource"]),
            [],
        ),
        (
            "Invalid with just UpdatePolicy",
            {"Type": "AWS::S3::Bucket", "DeletionPolicy": "Retain"},
            deque(["Resources", "MyResource"]),
            [
                ValidationError(
                    (
                        "Both 'UpdateReplacePolicy' and 'DeletionPolicy' are "
                        "needed to protect resource from deletion"
                    ),
                    path=deque([]),
                    rule=UpdateReplacePolicyDeletionPolicy(),
                    schema_path=deque(["anyOf"]),
                    validator="anyOf",
                    context=[],
                )
            ],
        ),
        (
            "Invalid with just UpdateReplacePolicy",
            {"Type": "AWS::S3::Bucket", "UpdateReplacePolicy": "Retain"},
            deque(["Resources", "MyResource"]),
            [
                ValidationError(
                    (
                        "Both 'UpdateReplacePolicy' and 'DeletionPolicy' are "
                        "needed to protect resource from deletion"
                    ),
                    path=deque([]),
                    rule=UpdateReplacePolicyDeletionPolicy(),
                    schema_path=deque(["anyOf"]),
                    validator="anyOf",
                    context=[],
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, validator):
    context = validator.context
    context = context.evolve(path=Path(path=path))
    validator = validator.evolve(context=context)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
