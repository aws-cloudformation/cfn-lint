"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.integration import BaseCliTestCase
import cfnlint.core


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing """

    scenarios = [
        {
            'filename': 'test/fixtures/templates/good/generic.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/minimal.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 4
                        },
                        "Path": [
                            "Resources",
                            "ExampleLayer29b0582575"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 4
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/bad/transform_serverless_template.yaml',
            'results': [
                {
                    'Filename': 'test/fixtures/templates/bad/transform_serverless_template.yaml',
                    'Location': {
                        'Start': {
                            'ColumnNumber': 1,
                            'LineNumber': 1
                        },
                        'End': {
                            'ColumnNumber': 1,
                            'LineNumber': 1
                        },
                        'Path': None
                    },
                    'Rule': {
                        'Id': 'E0001',
                        'Description': 'Errors found when performing transformation on the template',
                        'Source': 'https://github.com/aws-cloudformation/cfn-python-lint',
                        'ShortDescription': 'Error found when transforming the template'
                    },
                    'Level': 'Error',
                    'Message': 'Error transforming template: Resource with id [AppName] is invalid. Resource is missing the required [Location] property.'
                },
                {
                    'Filename': 'test/fixtures/templates/bad/transform_serverless_template.yaml',
                    'Location': {
                        'Start': {
                            'ColumnNumber': 1,
                            'LineNumber': 1
                        },
                        'End': {
                            'ColumnNumber': 1,
                            'LineNumber': 1
                        },
                        'Path': None
                    },
                    'Rule': {
                        'Id': 'E0001',
                        'Description': 'Errors found when performing transformation on the template',
                        'Source': 'https://github.com/aws-cloudformation/cfn-python-lint',
                        'ShortDescription': 'Error found when transforming the template'
                    },
                    'Level': 'Error',
                    'Message': "Error transforming template: Resource with id [ExampleLayer] is invalid. Missing required property 'ContentUri'."
                },
                {
                    'Filename': 'test/fixtures/templates/bad/transform_serverless_template.yaml',
                    'Location': {
                        'Start': {
                            'ColumnNumber': 1,
                            'LineNumber': 1
                        },
                        'End': {
                            'ColumnNumber': 1,
                            'LineNumber': 1
                        },
                        'Path': None
                    },
                    'Rule': {
                        'Id': 'E0001',
                        'Description': 'Errors found when performing transformation on the template',
                        'Source': 'https://github.com/aws-cloudformation/cfn-python-lint',
                        'ShortDescription': 'Error found when transforming the template'
                    },
                    'Level': 'Error',
                    'Message': "Error transforming template: Resource with id [myFunctionMyTimer] is invalid. Missing required property 'Schedule'."
                }
            ],
            'exit_code': 2,
        },
        {
            'filename': 'test/fixtures/templates/good/conditions.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/resources_codepipeline.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_api.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_api.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 4
                        },
                        "Path": [
                            "Resources",
                            "myFunctionVersionee13cf2679"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 4
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_function.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_function.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 4
                        },
                        "Path": [
                            "Resources",
                            "myFunctionVersionee13cf2679"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 4
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_globals.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_globals.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 9
                        },
                        "Path": [
                            "Resources",
                            "myFunctionVersionee13cf2679"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 9
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                },
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_globals.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {
                            "ColumnNumber": 13,
                            "LineNumber": 10
                        },
                        "Path": [
                            "Resources",
                            "myFunction",
                            "Properties",
                            "Runtime"
                        ],
                        "Start": {
                            "ColumnNumber": 3,
                            "LineNumber": 10
                        }
                    },
                    "Message": "Deprecated runtime (nodejs6.10) specified. Updating disabled since 2019-08-12, please consider to update to nodejs10.x",
                    "Rule": {
                        "Description": "Check if an EOL Lambda Runtime is specified and give an error if used. ",
                        "Id": "E2531",
                        "ShortDescription": "Check if EOL Lambda Function Runtimes are used",
                        "Source": "https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html"
                    }
                }
            ],
            'exit_code': 6,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform/list_transform.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 14
                        },
                        "Path": [
                            "Resources",
                            "SkillFunctionVersionb3d38083f6"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 14
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform_many.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform_not_sam.yaml',
            'results': [],
            'exit_code': 0,
        }
    ]

    def test_templates(self):
        """Test Successful JSON Parsing"""
        self.run_scenarios()

    def test_module_integration(self):
        """ Test same templates using integration approach"""
        rules = cfnlint.core.get_rules(
            [], [], ['E', 'W'], {}, False)
        self.run_module_integration_scenarios(rules)
