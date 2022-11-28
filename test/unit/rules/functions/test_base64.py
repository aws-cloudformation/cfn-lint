"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Base64 import Base64  # pylint: disable=E0401


class TestRulesBase64(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesBase64, self).setUp()
        self.collection.register(Base64())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions_base64.yaml", 1
        )
