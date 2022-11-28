"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.OnlyOne import OnlyOne  # pylint: disable=E0401


class TestPropertyOnlyOne(BaseRuleTestCase):
    """Test OnlyOne Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyOnlyOne, self).setUp()
        self.collection.register(OnlyOne())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/onlyone.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/onlyone.yaml", 4
        )
