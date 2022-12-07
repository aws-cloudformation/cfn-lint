"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ListDuplicatesAllowed import (
    ListDuplicatesAllowed,  # pylint: disable=E0401
)


class TestListDuplicatesAllowed(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestListDuplicatesAllowed, self).setUp()
        self.collection.register(ListDuplicatesAllowed())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/list_duplicates_allowed.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/list_duplicates_allowed.yaml",
            3,
        )
