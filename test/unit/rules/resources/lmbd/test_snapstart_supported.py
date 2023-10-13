"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.SnapStartSupported import SnapStartSupported


class TestSnapStartSupported(BaseRuleTestCase):
    """Test Lambda SnapStart supported"""

    def setUp(self):
        """Setup"""
        super(TestSnapStartSupported, self).setUp()
        self.collection.register(SnapStartSupported())
        self.success_templates = [
            "test/fixtures/templates/good/resources/lambda/snapstart-supported.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/snapstart-supported.yaml", 1
        )
