"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.context.context import Resource
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.DependsOn import DependsOn  # noqa: E501


@pytest.fixture(scope="module")
def rule():
    rule = DependsOn()
    yield rule


@pytest.fixture
def template():
    return {
        "Conditions": {
            "IsUsEast1": {
                "Fn::Equals": [
                    {"Ref": "AWS::Region"},
                    "us-east-1",
                ]
            }
        },
        "Resources": {
            "ParentBucket": {
                "Type": "AWS::S3::Bucket",
            },
            "ChildBucket": {
                "Type": "AWS::S3::Bucket",
                "DependsOn": "ParentBucket",
            },
            "ParentBucketWithGoodCondition": {
                "Condition": "IsUsEast1",
                "Type": "AWS::S3::Bucket",
            },
            "ChildBucketWithGoodCondition": {
                "Condition": "IsUsEast1",
                "DependsOn": "ParentBucketWithGoodCondition",
            },
            "ParentBucketWithBadCondition": {
                "Condition": "IsUsEast1",
                "Type": "AWS::S3::Bucket",
            },
            "ChildBucketWithBadCondition": {
                "Type": "AWS::S3::Bucket",
                "DependsOn": "ParentBucketWithBadCondition",
            },
            "ToMySelf": {
                "Type": "AWS::S3::Bucket",
                "DependsOn": "ToMySelf",
            },
        },
    }


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid depends on",
            "ParentBucket",
            deque(["Resources", "ChildBucket", "DependsOn"]),
            [],
        ),
        (
            "Invalid depends on but low path",
            "Foo",
            deque([]),
            [
                ValidationError(
                    "'Foo' is not one of ['ParentBucket', "
                    "'ChildBucket', "
                    "'ParentBucketWithGoodCondition', "
                    "'ParentBucketWithBadCondition', "
                    "'ChildBucketWithBadCondition', 'ToMySelf']",
                )
            ],
        ),
        (
            "Valid depends on with conditions",
            "ParentBucketWithGoodCondition",
            deque(["Resources", "ChildBucketWithGoodCondition", "DependsOn"]),
            [],
        ),
        (
            "Invalid type isn't validated by this rule",
            {"Ref": "MyResource"},
            deque(["Resources", "ChildBucket", "DependsOn"]),
            [],
        ),
        (
            "Invalid depends on",
            "Foo",
            deque(["Resources", "ChildBucket", "DependsOn"]),
            [
                ValidationError(
                    "'Foo' is not one of ['ParentBucket', "
                    "'ParentBucketWithGoodCondition', "
                    "'ParentBucketWithBadCondition', "
                    "'ChildBucketWithBadCondition', 'ToMySelf']",
                )
            ],
        ),
        (
            "Invalid depends on with conditions",
            "ParentBucketWithBadCondition",
            deque(["Resources", "ChildBucketWithBadCondition", "DependsOn"]),
            [
                ValidationError(
                    "'ParentBucketWithBadCondition' will not exist when condition "
                    "'IsUsEast1' is False",
                )
            ],
        ),
        (
            "Invalid depends on relying on itself",
            "ToMySelf",
            deque(["Resources", "ToMySelf", "DependsOn"]),
            [
                ValidationError(
                    "'ToMySelf' is not one of ['ParentBucket', 'ChildBucket', "
                    "'ParentBucketWithGoodCondition', "
                    "'ParentBucketWithBadCondition', 'ChildBucketWithBadCondition']",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, path, expected, rule, validator):
    validator = validator.evolve(context=validator.context.evolve(path=Path(path)))
    errs = list(rule.validate(validator, False, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"


def test_validate_with_no_cfn(rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(path=deque(["Resources", "ChildBucket", "DependsOn"]))
        )
    )
    validator.cfn = None
    errs = list(rule.validate(validator, False, "ParentBucketWithBadCondition", {}))

    assert errs == [], f"Test without cfn got {errs!r}"


def test_sam_module_subresource_skipped(rule, validator):
    """SAM-generated sub-resources are skipped like MODULE sub-resources.

    When DependsOn references a resource that starts with a SAM function name
    (e.g., MyFuncAliaslive for MyFunc of type AWS::Serverless::Function),
    validation is skipped because SAM generates many resources with dynamic
    names that can't be fully enumerated.
    """
    # Add a SAM function to the resources
    resources = dict(validator.context.resources)
    resources["MyFunc"] = Resource({"Type": "AWS::Serverless::Function"})

    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(path=deque(["Resources", "MyResource", "DependsOn"])),
            resources=resources,
        )
    )

    # DependsOn a SAM-generated alias (MyFuncAliaslive) - should be skipped
    errs = list(rule.validate(validator, False, "MyFuncAliaslive", {}))
    assert errs == [], "SAM sub-resource should be skipped"

    # DependsOn the SAM function itself - should still validate
    errs = list(rule.validate(validator, False, "MyFunc", {}))
    assert errs == [], "SAM function itself should be valid"

    # DependsOn a completely unknown resource - should error
    errs = list(rule.validate(validator, False, "TotallyUnknown", {}))
    assert len(errs) == 1, "Unknown resource should error"
    assert "TotallyUnknown" in errs[0].message
