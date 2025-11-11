"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.constants.RequiresTransform import RequiresTransform
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = RequiresTransform()
    yield rule


@pytest.mark.parametrize(
    "name,template,expected_matches",
    [
        (
            "No Constants section",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            0,
        ),
        (
            "Constants with LanguageExtensions transform (string)",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::LanguageExtensions",
                "Constants": {
                    "BucketPrefix": "my-bucket",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            0,
        ),
        (
            "Constants with LanguageExtensions transform (list)",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": [
                    "AWS::Serverless-2016-10-31",
                    "AWS::LanguageExtensions",
                ],
                "Constants": {
                    "BucketPrefix": "my-bucket",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            0,
        ),
        (
            "Constants without transform",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Constants": {
                    "BucketPrefix": "my-bucket",
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
            "Constants with wrong transform",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Constants": {
                    "BucketPrefix": "my-bucket",
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
            "Constants with list of wrong transforms",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": [
                    "AWS::Serverless-2016-10-31",
                    "AWS::Include",
                ],
                "Constants": {
                    "BucketPrefix": "my-bucket",
                },
                "Resources": {
                    "MyBucket": {
                        "Type": "AWS::S3::Bucket",
                    }
                },
            },
            1,
        ),
    ],
)
def test_requires_transform(name, template, expected_matches, rule):
    cfn = Template("", template, regions=["us-east-1"])
    matches = rule.match(cfn)
    
    assert len(matches) == expected_matches, (
        f"Test {name!r} expected {expected_matches} matches, got {len(matches)}"
    )
    
    if expected_matches > 0:
        assert matches[0].path == ["Constants"]
        assert "Transform: AWS::LanguageExtensions" in matches[0].message
