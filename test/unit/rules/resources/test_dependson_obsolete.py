"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.DependsOnObsolete import DependsOnObsolete


@pytest.fixture(scope="module")
def rule():
    rule = DependsOnObsolete()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "Parent1Bucket": {
                "Type": "AWS::S3::Bucket",
            },
            "Parent2Bucket": {
                "Type": "AWS::S3::Bucket",
            },
            "ChildBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": {"Ref": "Parent1Bucket"},
                },
            },
        },
    }


@pytest.fixture
def path():
    return Path(
        path=deque(["Resources", "ChildBucket", "DependsOn"]),
    )


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid depends on",
            "Parent2Bucket",
            [],
        ),
        (
            "Valid but wrong type",
            {},
            [],
        ),
        (
            "Obsolete depends on",
            "Parent1Bucket",
            [
                ValidationError(
                    (
                        "'Parent1Bucket' dependency already "
                        "enforced by a 'Ref' at "
                        "'Resources/ChildBucket/Properties/BucketName'"
                    ),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, False, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Obsolete depends on",
            "Parent1Bucket",
            [],
        ),
    ],
)
def test_validate_no_cfn_graph(name, instance, expected, rule, validator):

    validator.cfn.graph = None
    errs = list(rule.validate(validator, False, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
