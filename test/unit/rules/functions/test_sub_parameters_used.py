"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.SubParametersUsed import (
    SubParametersUsed,  # pylint: disable=E0401
)


class TestSubParametersUsed(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestSubParametersUsed, self).setUp()
        self.collection.register(SubParametersUsed())
        self.success_templates = [
            "test/fixtures/templates/good/functions/sub_parameters_used.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/sub_parameters_used.yaml", 1
        )
