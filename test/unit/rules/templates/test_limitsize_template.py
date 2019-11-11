"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.templates.LimitSize import LimitSize  # pylint: disable=E0401


class TestTemplateLimitSize(BaseRuleTestCase):
    """Test template limit size"""

    def setUp(self):
        """Setup"""
        super(TestTemplateLimitSize, self).setUp()
        self.collection.register(LimitSize())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/limit_size.yaml', 1)
