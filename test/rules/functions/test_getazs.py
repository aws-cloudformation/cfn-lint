"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.functions.GetAz import GetAz  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestRulesGetAZs(BaseRuleTestCase):
    """Test Rules Get Att """
    def setUp(self):
        """Setup"""
        super(TestRulesGetAZs, self).setUp()
        self.collection.register(GetAz())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/functions_getaz.yaml', 3)
