"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

import pytest

from cfnlint.rules.resources.lmbd.ZipPackageRequiredProperties import (
    ZipPackageRequiredProperties,
)
from cfnlint.template import Template


class TestZipPackageRequiredProperties(BaseRuleTestCase):
    """Test required properties"""

    def setUp(self):
        super(TestZipPackageRequiredProperties, self).setUp()
        self.collection.register(ZipPackageRequiredProperties())
        self.success_templates = [
            "test/fixtures/templates/good/resources/lambda/required_properties.yaml",
            "test/fixtures/templates/good/resources/lambda/sam_required_properties.yaml",
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/required_properties.yaml",
            err_count=3,
        )

    def test_file_negative_sam(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/sam_required_properties.yaml",
            err_count=4,
        )


@pytest.fixture(scope="module")
def rule():
    rule = ZipPackageRequiredProperties()
    yield rule


@pytest.mark.parametrize(
    "name,template,expected_count",
    [
        # SAM function with bare minimum (default Zip, no CodeUri/InlineCode/ImageUri)
        # This covers the else: pass branch (lines 121-125)
        (
            "SAM bare default Zip function missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "BareFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {},
                    },
                },
            },
            1,  # Missing both Handler and Runtime
        ),
        # SAM function with bare minimum but with Handler/Runtime (valid)
        (
            "SAM bare default Zip function with Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "BareFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "Handler": "index.handler",
                            "Runtime": "python3.9",
                        },
                    },
                },
            },
            0,
        ),
        # Lambda function with non-dict Properties (guard branch line 163-164)
        (
            "Lambda with non-dict Properties",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "BadFunction": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": "not-a-dict",
                    },
                },
            },
            0,  # Should skip, not error
        ),
        # SAM function with non-dict Properties (guard branch line 178-179)
        (
            "SAM with non-dict Properties",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "BadFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": ["not", "a", "dict"],
                    },
                },
            },
            0,  # Should skip, not error
        ),
        # Lambda function with intrinsic Ref in Properties
        # Note: {"Ref": "X"} is still a dict, so it passes the guard
        # but get_object_without_conditions will process it
        (
            "Lambda with Ref in Properties",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "RefFunction": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {"Ref": "SomeParameter"},
                    },
                },
            },
            0,  # Ref resolves to unknown, skipped as not Zip
        ),
        # SAM function with intrinsic Ref in Properties
        # Note: {"Ref": "X"} is still a dict, so it passes the guard
        (
            "SAM with Ref in Properties",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "RefFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {"Ref": "SomeParameter"},
                    },
                },
            },
            # This hits the else: pass branch
            # (no CodeUri/InlineCode/ImageUri/PackageType)
            # and reports missing Handler/Runtime
            1,
        ),
        # SAM Image function via PackageType (line 107-108)
        (
            "SAM Image via PackageType",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "ImageFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "PackageType": "Image",
                        },
                    },
                },
            },
            0,  # Image functions don't need Handler/Runtime
        ),
        # SAM Image function via ImageUri only (line 112-114)
        (
            "SAM Image via ImageUri",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "ImageFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "ImageUri": (
                                "123456789012.dkr.ecr.us-east-1.amazonaws.com/repo:tag"
                            ),
                        },
                    },
                },
            },
            0,  # Image functions don't need Handler/Runtime
        ),
        # SAM Zip function via CodeUri (line 115-117)
        (
            "SAM Zip via CodeUri missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "ZipFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "s3://bucket/code.zip",
                        },
                    },
                },
            },
            1,  # Missing Handler and Runtime
        ),
        # SAM Zip function via InlineCode (line 118-120)
        (
            "SAM Zip via InlineCode missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "ZipFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "InlineCode": "def handler(e, c): pass",
                        },
                    },
                },
            },
            1,  # Missing Handler and Runtime
        ),
        # SAM explicit PackageType: Zip (line 109-111)
        (
            "SAM explicit PackageType Zip missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "ZipFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "PackageType": "Zip",
                            "CodeUri": "s3://bucket/code.zip",
                        },
                    },
                },
            },
            1,  # Missing Handler and Runtime
        ),
        # Lambda with explicit PackageType: Zip (line 45-46)
        (
            "Lambda explicit PackageType Zip missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "ZipFunction": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "PackageType": "Zip",
                            "Role": "arn:aws:iam::123456789012:role/role",
                            "Code": {
                                "S3Bucket": "bucket",
                                "S3Key": "code.zip",
                            },
                        },
                    },
                },
            },
            1,  # Missing Handler and Runtime
        ),
        # Lambda with ZipFile in Code (line 47-48)
        (
            "Lambda with ZipFile missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "ZipFunction": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Role": "arn:aws:iam::123456789012:role/role",
                            "Code": {
                                "ZipFile": "def handler(e, c): pass",
                            },
                        },
                    },
                },
            },
            1,  # Missing Handler and Runtime
        ),
        # Lambda with S3Key in Code (line 47-48)
        (
            "Lambda with S3Key missing Handler/Runtime",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "ZipFunction": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Role": "arn:aws:iam::123456789012:role/role",
                            "Code": {
                                "S3Bucket": "bucket",
                                "S3Key": "code.zip",
                            },
                        },
                    },
                },
            },
            1,  # Missing Handler and Runtime
        ),
        # Lambda Image function (not Zip, line 49-50)
        (
            "Lambda Image function",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "ImageFunction": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "PackageType": "Image",
                            "Role": "arn:aws:iam::123456789012:role/role",
                            "Code": {
                                "ImageUri": (
                                    "123456789012.dkr.ecr.us-east-1.amazonaws.com"
                                    "/repo:tag"
                                ),
                            },
                        },
                    },
                },
            },
            0,  # Image functions don't need Handler/Runtime
        ),
        # Template with no Lambda/SAM functions
        (
            "Template with no functions",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "Bucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {},
                    },
                },
            },
            0,
        ),
    ],
)
def test_match(name, template, expected_count, rule):
    cfn = Template("", template, regions=["us-east-1"])
    matches = rule.match(cfn)
    assert len(matches) == expected_count, (
        f"Test {name!r}: expected {expected_count} matches, "
        f"got {len(matches)}: {matches}"
    )
