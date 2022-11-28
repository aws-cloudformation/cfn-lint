"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.FindInMapKeys import FindInMapKeys  # pylint: disable=E0401


class TestRulesFindInMapKeys(BaseRuleTestCase):
    """Test Find In Map Keys Rule"""

    def setUp(self):
        """Setup"""
        super(TestRulesFindInMapKeys, self).setUp()
        self.collection.register(FindInMapKeys())
        self.success_templates = [
            "test/fixtures/templates/good/functions/findinmap_keys.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/findinmap_keys.yaml", 3
        )
