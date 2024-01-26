"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.codepipeline.CodepipelineStages import (
    CodepipelineStages,  # pylint: disable=E0401
)


class TestCodePipelineStages(BaseRuleTestCase):
    """Test CodePipeline Stages Configuration"""

    def setUp(self):
        """Setup"""
        super(TestCodePipelineStages, self).setUp()
        self.collection.register(CodepipelineStages())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_onestage(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/stages_one_stage.yaml",
            2,
        )

    def test_file_negative_no_source(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/stages_no_source.yaml",
            1,
        )

    def test_file_negative_second_stage(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/stages_second_stage.yaml",
            1,
        )

    def test_file_negative_non_unique(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/stages_non_unique.yaml",
            1,
        )

    def test_file_negative_only_source_types(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/stages_only_source.yaml",
            2,
        )

    def test_scenario_format(self):
        """Test scenario formatting"""
        rule = CodepipelineStages()

        self.assertEqual(
            rule._format_error_message("Test.", {"Condition": True}),
            'Test. When condition "Condition" is True',
        )
        self.assertEqual(rule._format_error_message("Test.", None), "Test.")
