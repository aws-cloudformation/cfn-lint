"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.GetAtt import GetAtt  # pylint: disable=E0401


class TestRulesGetAtt(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesGetAtt, self).setUp()
        self.collection.register(GetAtt())
        self.success_templates = [
            "test/fixtures/templates/good/functions/getatt.yaml",
            "test/fixtures/templates/good/functions/modules_getatt.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/generic.yaml", 1)

    def test_file_negative_getatt(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/getatt.yaml", 7
        )
