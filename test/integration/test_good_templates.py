"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from test.integration import BaseCliTestCase

from cfnlint import ConfigMixIn


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing"""

    # ruff: noqa: E501
    scenarios = [
        {
            "filename": "test/fixtures/templates/good/generic.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/good/minimal.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/good/transform.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/issues/sam_w_conditions.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": (
                "test/fixtures/templates/bad/transform_serverless_template.yaml"
            ),
            "results": [
                {
                    "Filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
                    "Id": "9e05773a-b0d0-f157-2955-596d9bd54749",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 2, "LineNumber": 1},
                        "Path": None,
                        "Start": {"ColumnNumber": 1, "LineNumber": 1},
                    },
                    "Message": "Error transforming template: Resource with id [myFunctionMyTimer] is invalid. Missing required property 'Schedule'.",
                    "ParentId": None,
                    "Rule": {
                        "Description": "Errors found when performing transformation on the template",
                        "Id": "E0001",
                        "ShortDescription": "Error found when transforming the template",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
                    "Id": "fd751fa3-7d1f-e194-7108-eb08352814c8",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 2, "LineNumber": 1},
                        "Path": None,
                        "Start": {"ColumnNumber": 1, "LineNumber": 1},
                    },
                    "Message": "Error transforming template: Resource with id [ExampleLayer] is invalid. Missing required property 'ContentUri'.",
                    "ParentId": None,
                    "Rule": {
                        "Description": "Errors found when performing transformation on the template",
                        "Id": "E0001",
                        "ShortDescription": "Error found when transforming the template",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
                    "Id": "74181426-e865-10eb-96fd-908dfd30a358",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 2, "LineNumber": 1},
                        "Path": None,
                        "Start": {"ColumnNumber": 1, "LineNumber": 1},
                    },
                    "Message": "Error transforming template: Resource with id [AppName] is invalid. Resource is missing the required [Location] property.",
                    "ParentId": None,
                    "Rule": {
                        "Description": "Errors found when performing transformation on the template",
                        "Id": "E0001",
                        "ShortDescription": "Error found when transforming the template",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint",
                    },
                },
            ],
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/good/conditions.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/good/resources_codepipeline.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/good/resources_cognito_userpool_tag_is_string_map.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/bad/resources_cognito_userpool_tag_is_list.yaml",
            "results": [
                {
                    "Filename": str(
                        Path(
                            "test/fixtures/templates/bad/resources_cognito_userpool_tag_is_list.yaml"
                        )
                    ),
                    "Id": "3732b0a0-6d44-72af-860a-88e5f8ca790c",
                    "Level": "Error",
                    "Location": {
                        "Start": {"ColumnNumber": 7, "LineNumber": 16},
                        "End": {"ColumnNumber": 19, "LineNumber": 16},
                        "Path": [
                            "Resources",
                            "MyCognitoUserPool",
                            "Properties",
                            "UserPoolTags",
                        ],
                    },
                    "Message": (
                        "[{'Key': 'Key1', 'Value': 'Value1'}, {'Key': 'Key2', 'Value':"
                        " 'Value2'}] is not of type 'object'"
                    ),
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Checks resource property values with Primitive Types for"
                            " values that match those types."
                        ),
                        "Id": "E3012",
                        "ShortDescription": "Check resource properties values",
                        "Source": "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#type",
                    },
                }
            ],
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/good/transform_serverless_api.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform_serverless_function.yaml"
            ),
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform_serverless_globals.yaml"
            ),
            "results": [
                {
                    "Filename": str(
                        Path(
                            "test/fixtures/templates/good/transform_serverless_globals.yaml"
                        )
                    ),
                    "Id": "f0f6c586-81bc-9182-de02-659a3a1a5b2c",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 10},
                        "Path": ["Resources", "myFunction", "Properties", "Runtime"],
                        "Start": {"ColumnNumber": 3, "LineNumber": 10},
                    },
                    "Message": "Runtime 'nodejs6.10' was deprecated on '2019-08-12'. Creation was disabled on '2019-08-12' and update on '2019-08-12'. Please consider updating to 'nodejs20.x'",
                    "ParentId": None,
                    "Rule": {
                        "Description": (
                            "Check if an EOL Lambda Runtime is specified and you cannot update the function"
                        ),
                        "Id": "E2533",
                        "ShortDescription": (
                            "Check if Lambda Function Runtimes are updatable"
                        ),
                        "Source": "https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html",
                    },
                }
            ],
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/good/transform/list_transform.yaml",
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform/list_transform_many.yaml"
            ),
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform/list_transform_not_sam.yaml"
            ),
            "results": [],
            "exit_code": 0,
        },
    ]

    def test_templates(self):
        """Test Successful JSON Parsing"""
        self.run_scenarios()

    def test_module_integration(self):
        """Test same templates using integration approach"""
        self.run_module_integration_scenarios(
            ConfigMixIn([], include_checks=["W", "E"])
        )
