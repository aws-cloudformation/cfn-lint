"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.transforms.LanguageExtensionsBeforeSAM import (
    LanguageExtensionsBeforeSAM,  # pylint: disable=E0401
)


class TestLanguageExtensionsBeforeSAM(BaseRuleTestCase):
    """Test template limit size"""

    def setUp(self):
        """Setup"""
        super(TestLanguageExtensionsBeforeSAM, self).setUp()
        self.collection.register(LanguageExtensionsBeforeSAM())
        self.success_templates = [
            "test/fixtures/templates/good/transforms/language_extensions_with_sam.yaml",
            "test/fixtures/templates/good/transforms/string_transform.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/transforms/language_extensions_with_sam.yaml",
            1,
        )
