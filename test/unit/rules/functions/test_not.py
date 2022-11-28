"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Not import Not  # pylint: disable=E0401


class TestFunctionNot(BaseRuleTestCase):
    """Test Rules Get Not"""

    def setUp(self):
        """Setup"""
        super(TestFunctionNot, self).setUp()
        self.collection.register(Not())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/functions_not.yaml", 1)
