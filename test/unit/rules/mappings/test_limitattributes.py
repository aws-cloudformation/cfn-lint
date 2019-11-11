"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.mappings.LimitAttributes import LimitAttributes  # pylint: disable=E0401


class TestParameterLimitAttributes(BaseRuleTestCase):
    """Test parameters limit attributes"""

    def setUp(self):
        """Setup"""
        super(TestParameterLimitAttributes, self).setUp()
        self.collection.register(LimitAttributes())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/limit_numbers.yaml', 1)
