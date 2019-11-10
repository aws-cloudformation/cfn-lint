"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.integration import BaseCliTestCase


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing """

    scenarios = [
        {
            "filename": 'test/fixtures/templates/good/generic.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": 'test/fixtures/templates/good/minimal.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": 'test/fixtures/templates/good/transform.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": 'test/fixtures/templates/bad/transform_serverless_template.yaml',
            "results": [
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
            "exit_code": 2,
        },
        {
            "filename": 'test/fixtures/templates/good/conditions.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            'filename': 'test/fixtures/templates/good/resources_codepipeline.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_api.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_function.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_globals.yaml',
            "results": [
                {
                    'Level': 'Error',
                    'Message': 'Deprecated runtime (nodejs6.10) specified. Updating disabled since 2019-08-12, please consider to update to nodejs10.x',
                    'Location': {
                        'Path': ['Resources', 'myFunction', 'Properties', 'Runtime'],
                        'Start': {'LineNumber': 10, 'ColumnNumber': 3},
                        'End': {'LineNumber': 10, 'ColumnNumber': 13}
                    },
                    'Filename': 'test/fixtures/templates/good/transform_serverless_globals.yaml',
                    'Rule': {
                        'ShortDescription': 'Check if EOL Lambda Function Runtimes are used',
                        'Description': 'Check if an EOL Lambda Runtime is specified and give an error if used. ',
                        'Source': 'https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html',
                        'Id': 'E2531'
                    }
                }
            ],
            "exit_code": 2,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform_many.yaml',
            "results": [],
            "exit_code": 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform_not_sam.yaml',
            "results": [],
            "exit_code": 0,
        }
    ]

    def test_templates(self):
        """Test Successful JSON Parsing"""
        self.run_scenarios()
