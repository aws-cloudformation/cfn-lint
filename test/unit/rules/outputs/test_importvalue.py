"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.outputs.ImportValue import ImportValue  # pylint: disable=E0401


class TestOutputImportValue(BaseRuleTestCase):
    """Test Output ImportValue"""

    def setUp(self):
        """Setup"""
        super(TestOutputImportValue, self).setUp()
        self.collection.register(ImportValue())
        self.success_templates = [
            "test/fixtures/templates/good/outputs/importvalue.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/outputs/configuration.yaml", 1
        )
