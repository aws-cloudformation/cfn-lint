"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.SnapStart import SnapStart


class TestSnapStart(BaseRuleTestCase):
    """Test Lambda SnapStarts"""

    def setUp(self):
        """Setup"""
        super(TestSnapStart, self).setUp()
        self.collection.register(SnapStart())
        self.success_templates = [
            "test/fixtures/templates/good/resources/lambda/snapstart.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/snapstart.yaml", 2
        )
