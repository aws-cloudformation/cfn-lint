"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.codepipeline.CodepipelineStageActions import (
    CodepipelineStageActions,  # pylint: disable=E0401
)


class TestCodePipelineStageActions(BaseRuleTestCase):
    """Test CodePipeline Stage Actions Configuration"""

    def setUp(self):
        """Setup"""
        super(TestCodePipelineStageActions, self).setUp()
        self.collection.register(CodepipelineStageActions())
        self.success_templates = [
            "test/fixtures/templates/good/resources/codepipeline/stage_actions.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_artifact_counts(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/action_artifact_counts.yaml",
            5,
        )

    def test_file_invalid_version(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/action_invalid_version.yaml",
            3,
        )

    def test_file_non_unique(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/action_non_unique.yaml",
            1,
        )

    def test_output_artifact_names_unique(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/output_artifact_non_unique.yaml",
            1,
        )

    def test_input_artifact_names_exist(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codepipeline/input_artifact_not_exists.yaml",
            1,
        )
