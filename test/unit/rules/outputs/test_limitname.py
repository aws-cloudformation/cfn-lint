"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.outputs.LimitName import LimitName  # pylint: disable=E0401


class TestOutputLimitName(BaseRuleTestCase):
    """Test output limit name"""

    def setUp(self):
        """Setup"""
        super(TestOutputLimitName, self).setUp()
        self.collection.register(LimitName())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/limit_name.yaml", 1)
