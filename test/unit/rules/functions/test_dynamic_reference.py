"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.DynamicReferenceSecureString import (
    DynamicReferenceSecureString,  # pylint: disable=E0401
)


class TestDynamicReferenceSecureString(BaseRuleTestCase):
    """Test Rules Dynamic References exists"""

    def setUp(self):
        """Setup"""
        super(TestDynamicReferenceSecureString, self).setUp()
        self.collection.register(DynamicReferenceSecureString())
        self.success_templates = [
            "test/fixtures/templates/good/functions/dynamic_reference.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/dynamic_reference.yaml", 2
        )
