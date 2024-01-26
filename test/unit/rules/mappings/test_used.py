"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.mappings.Used import Used  # pylint: disable=E0401


class TestUsedMappings(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestUsedMappings, self).setUp()
        self.collection.register(Used())

    success_templates = [
        "test/fixtures/templates/good/functions_findinmap.yaml",
        "test/fixtures/templates/good/mappings/used.yaml",
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/mappings/used.yaml", 1)
