"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context, Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.SnapStart import SnapStart
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = SnapStart()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "GoodSnapStart": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {"S3Bucket": "XXXXXX", "S3Key": "key"},
                    "Handler": "handler",
                    "Role": "role",
                    "Runtime": "runtime",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                },
            },
            "GoodSnapStartVersion": {
                "Type": "AWS::Lambda::Version",
                "Properties": {"FunctionName": {"Ref": "GoodSnapStart"}},
            },
            "BadSnapStart": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {"S3Bucket": "XXXXXX", "S3Key": "key"},
                    "Handler": "handler",
                    "Role": "role",
                    "Runtime": "runtime",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                },
            },
            "GoodSamSnapStart": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "handler",
                    "Runtime": "python3.9",
                    "CodeUri": "s3://bucket/key",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                    "AutoPublishAlias": "live",
                },
            },
            "BadSamSnapStart": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "handler",
                    "Runtime": "python3.9",
                    "CodeUri": "s3://bucket/key",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                },
            },
            "GoodSamSnapStartIntrinsic": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "handler",
                    "Runtime": "python3.9",
                    "CodeUri": "s3://bucket/key",
                    "SnapStart": {"ApplyOn": "PublishedVersions"},
                    "AutoPublishAlias": {"Ref": "AliasName"},
                },
            },
            "SamSnapStartNone": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "handler",
                    "Runtime": "python3.9",
                    "CodeUri": "s3://bucket/key",
                    "SnapStart": {"ApplyOn": "None"},
                },
            },
        }
    }


@pytest.mark.parametrize(
    "name,instance,path,cfn_path,expected",
    [
        (
            "None type should result in no errors",
            "None",  # Not
            deque(["Resources", "BadSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            deque(
                [
                    "Resources",
                    "AWS::Lambda::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [],
        ),
        (
            "Wrong type should result in no errors",
            [],  # wrong type
            deque(["Resources", "BadSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            deque(
                [
                    "Resources",
                    "AWS::Lambda::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [],
        ),
        (
            "Correctly associated version to lambda function",
            "PublishedVersions",
            deque(["Resources", "GoodSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            deque(
                [
                    "Resources",
                    "AWS::Lambda::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [],
        ),
        (
            "Lambda function doesn't have version attached",
            "PublishedVersions",
            deque(["Resources", "BadSnapStart", "Properties", "SnapStart", "ApplyOn"]),
            deque(
                [
                    "Resources",
                    "AWS::Lambda::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [
                ValidationError(
                    "'SnapStart' is enabled but an 'AWS::Lambda::Version' "
                    "resource is not attached",
                )
            ],
        ),
        (
            "SAM function with AutoPublishAlias - valid",
            "PublishedVersions",
            deque(
                ["Resources", "GoodSamSnapStart", "Properties", "SnapStart", "ApplyOn"]
            ),
            deque(
                [
                    "Resources",
                    "AWS::Serverless::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [],
        ),
        (
            "SAM function without AutoPublishAlias - invalid",
            "PublishedVersions",
            deque(
                ["Resources", "BadSamSnapStart", "Properties", "SnapStart", "ApplyOn"]
            ),
            deque(
                [
                    "Resources",
                    "AWS::Serverless::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [
                ValidationError(
                    "'SnapStart' is enabled but 'AutoPublishAlias' is not configured",
                )
            ],
        ),
        (
            "SAM function with intrinsic AutoPublishAlias - valid",
            "PublishedVersions",
            deque(
                [
                    "Resources",
                    "GoodSamSnapStartIntrinsic",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            deque(
                [
                    "Resources",
                    "AWS::Serverless::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [],
        ),
        (
            "SAM function ApplyOn None - no error",
            "None",
            deque(
                ["Resources", "SamSnapStartNone", "Properties", "SnapStart", "ApplyOn"]
            ),
            deque(
                [
                    "Resources",
                    "AWS::Serverless::Function",
                    "Properties",
                    "SnapStart",
                    "ApplyOn",
                ]
            ),
            [],
        ),
    ],
)
def test_validate(name, instance, path, cfn_path, expected, rule, validator):
    validator = validator.evolve(
        context=Context(
            path=Path(
                path=path,
                cfn_path=cfn_path,
            )
        )
    )
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"{name!r}: expected {expected!r} got {errs!r}"


class TestSnapStartSamEdgeCases:
    """Test edge cases for SAM function handling"""

    @pytest.fixture
    def rule(self):
        return SnapStart()

    def test_sam_with_non_dict_properties(self, rule, validator):
        """Non-dict Properties should not cause errors"""
        template = {
            "Resources": {
                "MyFunction": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Ref": "SomeRef"},
                },
            }
        }
        validator = validator.evolve(
            cfn=Template("", template),
            context=Context(
                path=Path(
                    path=deque(
                        [
                            "Resources",
                            "MyFunction",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                    cfn_path=deque(
                        [
                            "Resources",
                            "AWS::Serverless::Function",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                )
            ),
        )
        errs = list(rule.validate(validator, "", "PublishedVersions", {}))
        assert errs == []

    def test_sam_with_non_dict_resource(self, rule, validator):
        """Non-dict resource should not cause errors"""
        template = {
            "Resources": {
                "MyFunction": {"Ref": "SomeRef"},
            }
        }
        validator = validator.evolve(
            cfn=Template("", template),
            context=Context(
                path=Path(
                    path=deque(
                        [
                            "Resources",
                            "MyFunction",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                    cfn_path=deque(
                        [
                            "Resources",
                            "AWS::Serverless::Function",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                )
            ),
        )
        errs = list(rule.validate(validator, "", "PublishedVersions", {}))
        assert errs == []

    def test_sam_with_intrinsic_resources(self, rule, validator):
        """Resources as intrinsic function should bail out without error"""
        template = {
            "Resources": {"Ref": "SomeRef"},
        }
        validator = validator.evolve(
            cfn=Template("", template),
            context=Context(
                path=Path(
                    path=deque(
                        [
                            "Resources",
                            "MyFunction",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                    cfn_path=deque(
                        [
                            "Resources",
                            "AWS::Serverless::Function",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                )
            ),
        )
        errs = list(rule.validate(validator, "", "PublishedVersions", {}))
        assert errs == []

    def test_sam_with_string_resources(self, rule, validator):
        """Resources as string should bail out without error (line 52)"""
        template = {
            "Resources": "not-a-dict",
        }
        validator = validator.evolve(
            cfn=Template("", template),
            context=Context(
                path=Path(
                    path=deque(
                        [
                            "Resources",
                            "MyFunction",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                    cfn_path=deque(
                        [
                            "Resources",
                            "AWS::Serverless::Function",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                )
            ),
        )
        errs = list(rule.validate(validator, "", "PublishedVersions", {}))
        assert errs == []

    def test_sam_with_string_resource(self, rule, validator):
        """Resource as string should bail out without error (line 61)"""
        template = {
            "Resources": {
                "MyFunction": "not-a-dict",
            }
        }
        validator = validator.evolve(
            cfn=Template("", template),
            context=Context(
                path=Path(
                    path=deque(
                        [
                            "Resources",
                            "MyFunction",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                    cfn_path=deque(
                        [
                            "Resources",
                            "AWS::Serverless::Function",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                )
            ),
        )
        errs = list(rule.validate(validator, "", "PublishedVersions", {}))
        assert errs == []

    def test_sam_with_string_properties(self, rule, validator):
        """Properties as string should bail out without error (line 70)"""
        template = {
            "Resources": {
                "MyFunction": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": "not-a-dict",
                },
            }
        }
        validator = validator.evolve(
            cfn=Template("", template),
            context=Context(
                path=Path(
                    path=deque(
                        [
                            "Resources",
                            "MyFunction",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                    cfn_path=deque(
                        [
                            "Resources",
                            "AWS::Serverless::Function",
                            "Properties",
                            "SnapStart",
                            "ApplyOn",
                        ]
                    ),
                )
            ),
        )
        errs = list(rule.validate(validator, "", "PublishedVersions", {}))
        assert errs == []
