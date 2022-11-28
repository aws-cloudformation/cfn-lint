"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.iam.Permissions import Permissions  # pylint: disable=E0401


class TestPermissions(BaseRuleTestCase):
    """Test IAM Resource Policies"""

    def setUp(self):
        """Setup"""
        super(TestPermissions, self).setUp()
        self.collection.register(Permissions())

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/iam/managed_policy_permissions.yaml",
            3,
        )
