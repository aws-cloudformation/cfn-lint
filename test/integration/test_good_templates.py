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
            "results_filename": "test/fixtures/results/good/generic_yaml.json",
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/good/minimal.yaml",
            "results_filename": "test/fixtures/results/good/minimal_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": "test/fixtures/templates/good/transform.yaml",
            "results_filename": "test/fixtures/results/good/transform_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": "test/fixtures/templates/issues/sam_w_conditions.yaml",
            "results_filename": "test/fixtures/results/issues/sam_w_conditions_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/bad/transform_serverless_template.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/good/transform_serverless_template.json"
            ),
            "exit_code": 6,
        },
        {
            "filename": "test/fixtures/templates/good/conditions.yaml",
            "results_filename": "test/fixtures/results/good/conditions_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": "test/fixtures/templates/good/resources_codepipeline.yaml",
            "results_filename": "test/fixtures/results/good/resources_codepipeline_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/resources_cognito_userpool_tag_is_string_map.yaml"
            ),
            "results_filename": "test/fixtures/results/good/resources_cognito_userpool_tag_is_string_map_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/bad/resources_cognito_userpool_tag_is_list.yaml"
            ),
            "results_filename": "test/fixtures/results/bad/resources_cognito_userpool_tag_is_list_yaml.json",
            "exit_code": 6,
        },
        {
            "filename": "test/fixtures/templates/good/transform_serverless_api.yaml",
            "results_filename": "test/fixtures/results/good/transform_serverless_api_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform_serverless_function.yaml"
            ),
            "results_filename": "test/fixtures/results/good/transform_serverless_function_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform_serverless_globals.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/good/transform_serverless_globals.json"
            ),
            "exit_code": 6,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform_serverless_ignore_globals.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/good/transform_serverless_ignore_globals.json"
            ),
            "exit_code": 6,
        },
        {
            "filename": "test/fixtures/templates/good/transform/list_transform.yaml",
            "results_filename": "test/fixtures/results/good/transform/list_transform_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform/list_transform_many.yaml"
            ),
            "results_filename": "test/fixtures/results/good/transform/list_transform_many_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/transform/list_transform_not_sam.yaml"
            ),
            "results_filename": "test/fixtures/results/good/transform/list_transform_not_sam_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/functions/get_stack_output.yaml"
            ),
            "results_filename": "test/fixtures/results/good/functions/get_stack_output_yaml.json",
                        "exit_code": 4,
        },
        {
            "filename": (
                "test/fixtures/templates/good/functions/"
                "getatt_serverless_function_version.yaml"
            ),
            "results_filename": "test/fixtures/results/good/functions/getatt_serverless_function_version_yaml.json",
            "exit_code": 4,
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
