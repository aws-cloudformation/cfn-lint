"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.functions.Select import Select  # pylint: disable=E0401


class TestRulesSelect(BaseRuleTestCase):
    """Test Rules Get Att """

    def setUp(self):
        """Setup"""
        super(TestRulesSelect, self).setUp()
        self.collection.register(Select())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/functions_select.yaml', 3)
