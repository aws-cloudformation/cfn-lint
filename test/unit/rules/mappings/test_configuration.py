"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.mappings.Configuration import Configuration  # pylint: disable=E0401


class TestMappingConfiguration(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestMappingConfiguration, self).setUp()
        self.collection.register(Configuration())
        self.success_templates = [
            "test/fixtures/templates/good/mappings/configuration.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/mappings/configuration.yaml", 6
        )
