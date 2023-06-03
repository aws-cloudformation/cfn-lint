"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from test.integration import BaseCliTestCase


class TestDirectives(BaseCliTestCase):
    """Test Directives"""

    # ruff: noqa: E501
    scenarios = [
        {
            "filename": str(Path("test/fixtures/templates/good/core/directives.yaml")),
            "exit_code": 0,
            "results": [],
        },
        {
            "filename": str(Path("test/fixtures/templates/bad/core/directives.yaml")),
            "exit_code": 2,
            "results": [
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 18, "LineNumber": 17},
                        "Path": [
                            "Resources",
                            "myBucketFail",
                            "Properties",
                            "BucketName1",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 17},
                    },
                    "Message": "Additional properties are not allowed ('BucketName1' was unexpected)",
                    "Rule": {
                        "Description": (
                            "Making sure that resources properties are properly"
                            " configured"
                        ),
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are invalid",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties",
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 28},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastPass",
                            "Properties",
                            "BadKey",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 28},
                    },
                    "Message": "Additional properties are not allowed ('BadKey' was unexpected)",
                    "Rule": {
                        "Description": (
                            "Making sure that resources properties are properly"
                            " configured"
                        ),
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are invalid",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties",
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 16, "LineNumber": 32},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastFail",
                            "BadProperty",
                        ],
                        "Start": {"ColumnNumber": 5, "LineNumber": 32},
                    },
                    "Message": "Additional properties are not allowed ('BadProperty' was unexpected)",
                    "Rule": {
                        "Description": (
                            "Making sure the basic CloudFormation resources are"
                            " properly configured"
                        ),
                        "Id": "E3001",
                        "ShortDescription": "Basic CloudFormation Resource Check",
                        "Source": (
                            "https://github.com/aws-cloudformation/cfn-python-lint"
                        ),
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 35},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastFail",
                            "Properties",
                            "BadKey",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 35},
                    },
                    "Message": "Additional properties are not allowed ('BadKey' was unexpected)",
                    "Rule": {
                        "Description": (
                            "Making sure that resources properties are properly"
                            " configured"
                        ),
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are invalid",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties",
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 15, "LineNumber": 37},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastFail",
                            "Properties",
                            "VersioningConfiguration",
                            "Status",
                        ],
                        "Start": {"ColumnNumber": 9, "LineNumber": 37},
                    },
                    "Message": "'Enabled1' is not one of ['Enabled', 'Suspended']",
                    "Rule": {
                        "Description": (
                            "Check if properties have a valid value in case of an"
                            " enumator"
                        ),
                        "Id": "E3030",
                        "ShortDescription": "Check if properties have a valid value",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue",
                    },
                },
            ],
        },
    ]

    def test_templates(self):
        """Test ignoring certain rules"""
        self.run_scenarios()
