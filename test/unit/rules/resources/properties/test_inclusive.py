"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.Inclusive import (
    Inclusive,  # pylint: disable=E0401
)


class TestPropertyInclusive(BaseRuleTestCase):
    """Test Inclusive Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyInclusive, self).setUp()
        self.collection.register(Inclusive())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/inclusive.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/inclusive.yaml", 6
        )
