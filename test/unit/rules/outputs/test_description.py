"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.outputs.Description import Description  # pylint: disable=E0401


class TestDescription(BaseRuleTestCase):
    """Test Output Description"""

    def setUp(self):
        """Setup"""
        super(TestDescription, self).setUp()
        self.collection.register(Description())
        self.success_templates = [
            "test/fixtures/templates/good/outputs/description.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/outputs/description.yaml", 1
        )
