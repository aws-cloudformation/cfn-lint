"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.conditions.EqualsIsUseful import (
    EqualsIsUseful,  # pylint: disable=E0401
)


class TestEqualsIsUseful(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestEqualsIsUseful, self).setUp()
        self.collection.register(EqualsIsUseful())

    success_templates = []

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/conditions/equals_not_useful.yaml", 3
        )
