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
                    "Id": "4d8d1fd7-496f-9420-44df-f053d372c3be",
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
                    "Message": "Additional properties are not allowed ('BucketName1' was unexpected. Did you mean 'BucketName'?)",
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Making sure that resources properties are properly"
                            " configured"
                        ),
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are invalid",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#properties",
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Id": "dd126795-8106-b986-19ed-db769ee48fba",
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
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Making sure that resources properties are properly"
                            " configured"
                        ),
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are invalid",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#properties",
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Id": "431970a8-482e-2aca-af3f-5d4f819f0b45",
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
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Making sure the basic CloudFormation resources are"
                            " properly configured"
                        ),
                        "Id": "E3001",
                        "ShortDescription": "Basic CloudFormation Resource Check",
                        "Source": ("https://github.com/aws-cloudformation/cfn-lint"),
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Id": "814e8b07-dcef-f3ac-4285-8032d1fb010e",
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
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Making sure that resources properties are properly"
                            " configured"
                        ),
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are invalid",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#properties",
                    },
                },
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/directives.yaml")
                    ),
                    "Id": "2637b826-b8a7-4e03-8b27-bf8e8d4d12ee",
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
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Check if properties have a valid value in case of an"
                            " enumator"
                        ),
                        "Id": "E3030",
                        "ShortDescription": "Check if properties have a valid value",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#enum",
                    },
                },
            ],
        },
    ]

    def test_templates(self):
        """Test ignoring certain rules"""
        self.run_scenarios()
