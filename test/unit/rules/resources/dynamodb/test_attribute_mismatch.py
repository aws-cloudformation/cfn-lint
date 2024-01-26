"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.dynamodb.AttributeMismatch import (
    AttributeMismatch,  # pylint: disable=E0401
)


class TestAttributeMismatch(BaseRuleTestCase):
    """Test AttributeMisMatch"""

    def setUp(self):
        """Setup"""
        super(TestAttributeMismatch, self).setUp()
        self.collection.register(AttributeMismatch())
        self.success_templates = [
            "test/fixtures/templates/good/resources/dynamodb/attributes.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_unused_1(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/dynamodb/unused_attribute_definition_1.yaml",
            1,
        )

    def test_file_negative_unused_2(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/dynamodb/unused_attribute_definition_2.yaml",
            1,
        )

    def test_file_negative_undefined(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/dynamodb/undefined_attribute_definition.yaml",
            1,
        )
