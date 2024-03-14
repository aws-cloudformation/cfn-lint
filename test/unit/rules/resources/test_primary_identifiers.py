"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

# ruff: noqa: E501
from cfnlint.rules.resources.PrimaryIdentifiers import PrimaryIdentifiers


class TestPrimaryIdentifiers(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestPrimaryIdentifiers, self).setUp()
        self.collection.register(PrimaryIdentifiers())
        self.success_templates = [
            "test/fixtures/templates/good/resources/primary_identifiers.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/primary_identifiers.yaml", 8
        )
