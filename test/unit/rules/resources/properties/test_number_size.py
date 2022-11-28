"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.NumberSize import (
    NumberSize,  # pylint: disable=E0401
)


class TestNumberSize(BaseRuleTestCase):
    """Test Number Size Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestNumberSize, self).setUp()
        self.collection.register(NumberSize())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/number_size.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_string_size(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/number_size.yaml", 7
        )
