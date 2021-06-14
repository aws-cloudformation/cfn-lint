"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.integration import BaseCliTestCase


class TestDirectives(BaseCliTestCase):
    """Test Directives """

    scenarios = [
        {
            "filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
            "exit_code": 2,
            "results": [
                {
                    "Filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
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
                    "Message": "Invalid Property Resources/myBucketFail/Properties/BucketName1",
                    "Rule": {
                        "Description": "Making sure that resources properties are properly configured",
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are valid",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
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
                    "Message": "Invalid Property Resources/myBucketFirstAndLastPass/Properties/BadKey",
                    "Rule": {
                        "Description": "Making sure that resources properties are properly configured",
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are valid",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
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
                    "Message": "Invalid resource attribute BadProperty for resource myBucketFirstAndLastFail",
                    "Rule": {
                        "Description": "Making sure the basic CloudFormation resources are properly configured",
                        "Id": "E3001",
                        "ShortDescription": "Basic CloudFormation Resource Check",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
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
                    "Message": "Invalid Property Resources/myBucketFirstAndLastFail/Properties/BadKey",
                    "Rule": {
                        "Description": "Making sure that resources properties are properly configured",
                        "Id": "E3002",
                        "ShortDescription": "Resource properties are valid",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/core/mandatory_checks.yaml",
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
                    "Message": 'You must specify a valid value for Status (Enabled1). Valid values are ["Enabled", "Suspended"]',
                    "Rule": {
                        "Description": "Check if properties have a valid value in case of an enumator",
                        "Id": "E3030",
                        "ShortDescription": "Check if properties have a valid value",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue",
                    },
                },
                {
                    'Filename': 'test/fixtures/templates/bad/core/mandatory_checks.yaml',
                    'Level': 'Error',
                    'Location': {
                        'End': {'ColumnNumber': 18, 'LineNumber': 13},
                        'Path': [
                            'Resources',
                            'myBucketPass',
                            'Properties',
                            'BucketName1'
                        ],
                        'Start': {'ColumnNumber': 7, 'LineNumber': 13}
                    },
                    'Message': 'Invalid Property Resources/myBucketPass/Properties/BucketName1',
                    'Rule': {
                        'Description': 'Making sure that resources properties are properly configured',
                        'Id': 'E3002',
                        'ShortDescription': 'Resource properties are valid',
                        'Source': 'https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties'
                        }
                    },
                {
                    'Filename': 'test/fixtures/templates/bad/core/mandatory_checks.yaml',
                    'Level': 'Error',
                    'Location': {
                        'End': {'ColumnNumber': 16, 'LineNumber': 19},
                        'Path': [
                            'Resources',
                            'myBucketFirstAndLastPass',
                            'BadProperty'
                        ],
                        'Start': {'ColumnNumber': 5, 'LineNumber': 19}
                    },
                    'Message': 'Invalid resource attribute BadProperty for resource myBucketFirstAndLastPass',
                    'Rule': {
                        'Description': 'Making sure the basic CloudFormation resources are properly configured',
                        'Id': 'E3001',
                        'ShortDescription': 'Basic CloudFormation Resource Check',
                        'Source': 'https://github.com/aws-cloudformation/cfn-python-lint'
                    }
                }
            ],
        }
    ]

    def test_templates_explicit(self):
        """Test making certain rules mandatory explictly"""
        self.run_scenarios(["--mandatory-checks", "E3001", "E3002"])

    def test_templates_prefixed(self):
        """Test making certain rules mandatory via a rule prefix"""
        self.run_scenarios(["--mandatory-checks", "E300"])
