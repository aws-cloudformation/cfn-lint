"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.SubNotJoin import SubNotJoin  # pylint: disable=E0401


class TestSubNotJoin(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestSubNotJoin, self).setUp()
        self.collection.register(SubNotJoin())
        self.success_templates = [
            "test/fixtures/templates/good/functions/subnotjoin.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/subnotjoin.yaml", 1
        )
