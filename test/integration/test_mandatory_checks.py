"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from test.integration import BaseCliTestCase
from typing import Any, Dict, List


class TestDirectives(BaseCliTestCase):
    """Test Directives"""

    # ruff: noqa: E501
    scenarios: List[Dict[str, Any]] = [
        {
            "filename": str(
                Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
            ),
            "exit_code": 2,
            "results": [
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "c93c312c-c623-117a-7085-9d03d9f6a3af",
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
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "8d22c4cc-c440-b845-21de-ec27bde90312",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 23},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastPass",
                            "Properties",
                            "BadKey",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 23},
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
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "114825b2-3b6f-b2dc-945a-8ad2ea0a4dc2",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 16, "LineNumber": 27},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastFail",
                            "BadProperty",
                        ],
                        "Start": {"ColumnNumber": 5, "LineNumber": 27},
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
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "a89a2538-9395-c5fa-df78-390412c8042f",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 30},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastFail",
                            "Properties",
                            "BadKey",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 30},
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
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "be85985f-7f5a-03d9-2974-684226bbe38b",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 15, "LineNumber": 25},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastPass",
                            "Properties",
                            "VersioningConfiguration",
                            "Status",
                        ],
                        "Start": {"ColumnNumber": 9, "LineNumber": 25},
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
                {
                    "Filename": str(
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "fba65f07-d001-40c3-ea91-df14792b2649",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 18, "LineNumber": 13},
                        "Path": [
                            "Resources",
                            "myBucketPass",
                            "Properties",
                            "BucketName1",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 13},
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
                        Path("test/fixtures/templates/bad/core/mandatory_checks.yaml")
                    ),
                    "Id": "2449357e-568a-5c23-5cef-88381662e53c",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 16, "LineNumber": 19},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastPass",
                            "BadProperty",
                        ],
                        "Start": {"ColumnNumber": 5, "LineNumber": 19},
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
                    "Id": "790d09d4-4c82-7a75-89c1-fef2f13d2dcb",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 15, "LineNumber": 32},
                        "Path": [
                            "Resources",
                            "myBucketFirstAndLastFail",
                            "Properties",
                            "VersioningConfiguration",
                            "Status",
                        ],
                        "Start": {"ColumnNumber": 9, "LineNumber": 32},
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
        }
    ]

    def test_templates_explicit(self):
        """Test making certain rules mandatory explictly"""
        self.run_scenarios(["--mandatory-checks", "E3001", "E3002"])

    def test_templates_prefixed(self):
        """Test making certain rules mandatory via a rule prefix"""
        self.run_scenarios(["--mandatory-checks", "E300"])
