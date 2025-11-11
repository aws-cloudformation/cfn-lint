"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.constants.Used import Used
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Used()
    yield rule


@pytest.mark.parametrize(
    "name,template,expected_matches",
    [
        (
            "No Constants section",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            0,
        ),
        (
            "Constants without LanguageExtensions transform",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Constants": {
                    "UnusedConstant": "value",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            0,  # Rule doesn't run without transform
        ),
        (
            "Constant used in Fn::Sub",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Constants": {
                    "BucketPrefix": "my-bucket",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                            "BucketName": {"Fn::Sub": "${BucketPrefix}-bucket"}
                        }
                    }
                },
            },
            0,
        ),
        (
            "Constant used in Fn::Sub with map",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Constants": {
                    "Environment": "prod",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                            "BucketName": {
                                "Fn::Sub": [
                                    "${Prefix}-${Environment}",
                                    {"Prefix": "my-bucket"}
                                ]
                            }
                        }
                    }
                },
            },
            0,
        ),
        (
            "Constant used in Ref",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Constants": {
                    "BucketName": "my-bucket",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                            "BucketName": {"Ref": "BucketName"}
                        }
                    }
                },
            },
            0,
        ),
        (
            "Unused constant",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Constants": {
                    "UnusedConstant": "value",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            1,
        ),
        (
            "Multiple constants - some used, some unused",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Constants": {
                    "UsedConstant": "used",
                    "UnusedConstant1": "unused1",
                    "UnusedConstant2": "unused2",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                            "BucketName": {"Fn::Sub": "${UsedConstant}-bucket"}
                        }
                    }
                },
            },
            2,
        ),
    ],
)
def test_used(name, template, expected_matches, rule):
    cfn = Template("", template, regions=["us-east-1"])
    matches = rule.match(cfn)
    
    assert len(matches) == expected_matches, (
        f"Test {name!r} expected {expected_matches} matches, got {len(matches)}: {matches}"
    )
    
    if expected_matches > 0:
        for match in matches:
            assert match.path[0] == "Constants"
            assert "not used" in match.message
