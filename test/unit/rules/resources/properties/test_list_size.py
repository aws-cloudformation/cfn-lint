"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ListSize import (
    ListSize,  # pylint: disable=E0401
)


class TestListSize(BaseRuleTestCase):
    """Test List Size Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestListSize, self).setUp()
        self.collection.register(ListSize())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_iam_managed_policies(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_iam_managedpolicyarns.yaml", 3
        )

    def test_file_negative_iam_user_groups(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_iam_user_groups.yaml", 1
        )
