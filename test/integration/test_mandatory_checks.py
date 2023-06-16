"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.integration import BaseCliTestCase
from typing import Any, Dict, List


class TestDirectives(BaseCliTestCase):
    """Test Directives"""

    # ruff: noqa: E501
    scenarios: List[Dict[str, Any]] = [
        {
            "filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
            "exit_code": 2,
            "results": [
                {
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
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
                    "Message": "Additional properties are not allowed ('BucketName1' was unexpected. Did you mean 'BucketName'?)",
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
                {
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
                    "Filename": (
                        "test/fixtures/templates/bad/core/mandatory_checks.yaml"
                    ),
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
        }
    ]

    def test_templates_explicit(self):
        """Test making certain rules mandatory explictly"""
        self.run_scenarios(["--mandatory-checks", "E3001", "E3002"])

    def test_templates_prefixed(self):
        """Test making certain rules mandatory via a rule prefix"""
        self.run_scenarios(["--mandatory-checks", "E300"])
