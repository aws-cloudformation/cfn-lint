"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.functions.RefExist import RefExist  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestRulesRefExist(BaseRuleTestCase):
    """Test Rules Ref exists """
    def setUp(self):
        """Setup"""
        super(TestRulesRefExist, self).setUp()
        self.collection.register(RefExist())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/functions/ref.yaml', 3)
