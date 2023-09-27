"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.Exclusive import (
    Exclusive,  # pylint: disable=E0401
)


class TestPropertyExclusive(BaseRuleTestCase):
    """Test Exclusive Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyExclusive, self).setUp()
        self.collection.register(Exclusive())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/exclusive.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/exclusive.yaml", 3
        )
