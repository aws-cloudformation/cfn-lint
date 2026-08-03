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
            "results_filename": (
                "test/fixtures/results/good/transform_serverless_template.json"
            ),
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
            "filename": (
                "test/fixtures/templates/good/resources_cognito_userpool_tag_is_string_map.yaml"
            ),
            "results": [],
            "exit_code": 0,
        },
        {
            "filename": (
                "test/fixtures/templates/bad/resources_cognito_userpool_tag_is_list.yaml"
            ),
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
                        "Source": (
                            "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#type"
                        ),
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
            "results_filename": (
                "test/fixtures/results/good/transform_serverless_globals.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform_serverless_ignore_globals.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/good/transform_serverless_ignore_globals.json"
            ),
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
        {
            "filename": (
                "test/fixtures/templates/good/functions/get_stack_output.yaml"
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
