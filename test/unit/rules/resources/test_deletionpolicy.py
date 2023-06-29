"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.DeletionPolicy import (
    DeletionPolicy,  # pylint: disable=E0401
)


class TestResourceDeletionPolicy(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestResourceDeletionPolicy, self).setUp()
        self.collection.register(DeletionPolicy())
        self.success_templates = [
            "test/fixtures/templates/good/resources_deletionpolicy.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_deletionpolicy.yaml", 5
        )
