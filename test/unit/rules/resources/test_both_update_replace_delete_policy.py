"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Resource
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.BothUpdateReplacePolicyDeletionPolicyNeeded import (
    UpdateReplacePolicyDeletionPolicy,
)


@pytest.fixture(scope="module")
def rule():
    rule = UpdateReplacePolicyDeletionPolicy()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={
            "MyResource": Resource({"Type": "AWS::S3::Bucket"}),
        },
        parameters={},
    )
    yield CfnTemplateValidator(context=context)


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
                "DeletionPolicy": "Retain",
                "UpdateReplacePolicy": "Retain",
            },
            deque(["Resources", "MyResource"]),
            [],
        ),
        (
            "Invalid with just UpdatePolicy",
            {"DeletionPolicy": "Retain"},
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
                    context=[
                        ValidationError(
                            "'Delete' was expected",
                            validator="const",
                            schema_path=deque(
                                [0, "properties", "DeletionPolicy", "const"]
                            ),
                            path=deque(["DeletionPolicy"]),
                        ),
                        ValidationError(
                            "False schema does not allow 'Retain'",
                            schema_path=deque([1, "properties", "DeletionPolicy"]),
                            path=deque(["DeletionPolicy"]),
                            validator=None,
                        ),
                        ValidationError(
                            "'UpdateReplacePolicy' is a required property",
                            validator="required",
                            schema_path=deque([2, "required"]),
                        ),
                        ValidationError(
                            "False schema does not allow 'Retain'",
                            schema_path=deque([3, "properties", "DeletionPolicy"]),
                            path=deque(["DeletionPolicy"]),
                            validator=None,
                        ),
                    ],
                )
            ],
        ),
        (
            "Invalid with just UpdateReplacePolicy",
            {"UpdateReplacePolicy": "Retain"},
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
                    context=[
                        ValidationError(
                            "False schema does not allow 'Retain'",
                            schema_path=deque([0, "properties", "UpdateReplacePolicy"]),
                            path=deque(["UpdateReplacePolicy"]),
                            validator=None,
                        ),
                        ValidationError(
                            "'Delete' was expected",
                            validator="const",
                            schema_path=deque(
                                [1, "properties", "UpdateReplacePolicy", "const"]
                            ),
                            path=deque(["UpdateReplacePolicy"]),
                        ),
                        ValidationError(
                            "'DeletionPolicy' is a required property",
                            validator="required",
                            schema_path=deque([2, "required"]),
                        ),
                        ValidationError(
                            "False schema does not allow 'Retain'",
                            schema_path=deque([3, "properties", "UpdateReplacePolicy"]),
                            path=deque(["UpdateReplacePolicy"]),
                            validator=None,
                        ),
                    ],
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, validator):
    context = validator.context
    for p in path:
        context = context.evolve(path=p)
    validator = validator.evolve(context=context)
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
