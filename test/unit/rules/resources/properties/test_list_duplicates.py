"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ListDuplicates import (
    ListDuplicates,  # pylint: disable=E0401
)


class TestListDuplicates(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestListDuplicates, self).setUp()
        self.collection.register(ListDuplicates())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/list_duplicates.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/list_duplicates.yaml", 4
        )
