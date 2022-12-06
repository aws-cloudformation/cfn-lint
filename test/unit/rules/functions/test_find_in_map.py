"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.FindInMap import FindInMap  # pylint: disable=E0401


class TestRulesFindInMap(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesFindInMap, self).setUp()
        self.collection.register(FindInMap())
        self.success_templates = [
            "test/fixtures/templates/good/functions_findinmap.yaml",
            "test/fixtures/templates/good/functions_findinmap_enhanced.yaml",
            "test/fixtures/templates/good/functions_findinmap_default_value.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions_findinmap.yaml", 7
        )

    def test_file_negative_enhanced(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions_findinmap_default_value.yaml", 15
        )
