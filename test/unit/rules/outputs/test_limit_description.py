"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.outputs.LimitDescription import (
    LimitDescription,  # pylint: disable=E0401
)


class TestLimitDescription(BaseRuleTestCase):
    """Test Output Description"""

    def setUp(self):
        """Setup"""
        super(TestLimitDescription, self).setUp()
        self.collection.register(LimitDescription())
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
