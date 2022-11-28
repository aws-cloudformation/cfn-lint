"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Cidr import Cidr  # pylint: disable=E0401


class TestRulesCidr(BaseRuleTestCase):
    """Test Cidr Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesCidr, self).setUp()
        self.collection.register(Cidr())
        self.success_templates = [
            "test/fixtures/templates/good/functions_cidr.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_positive_extra(self):
        """Test failure"""
        self.helper_file_positive_template(
            "test/fixtures/templates/good/functions/cidr.yaml"
        )

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/functions_cidr.yaml", 11)
