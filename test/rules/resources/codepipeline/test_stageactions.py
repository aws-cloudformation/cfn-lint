"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint.rules.resources.codepipeline.CodepipelineStageActions import CodepipelineStageActions  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestCodePipelineStageActions(BaseRuleTestCase):
    """Test CodePipeline Stage Actions Configuration"""
    def setUp(self):
        """Setup"""
        super(TestCodePipelineStageActions, self).setUp()
        self.collection.register(CodepipelineStageActions())
        self.success_templates = [
            'test/fixtures/templates/good/resources/codepipeline/stage_actions.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_artifact_counts(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources/codepipeline/action_artifact_counts.yaml', 4)

    def test_file_invalid_version(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources/codepipeline/action_invalid_version.yaml', 3)

    def test_file_non_unique(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources/codepipeline/action_non_unique.yaml', 1)
