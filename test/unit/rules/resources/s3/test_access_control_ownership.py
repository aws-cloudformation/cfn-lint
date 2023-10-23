"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.s3.AccessControlOwnership import AccessControlOwnership


class TestAccessControlOwnership(BaseRuleTestCase):
    """Test Lambda Trigger Events CloudWatchLogs Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestAccessControlOwnership, self).setUp()
        self.collection.register(AccessControlOwnership())
        self.success_templates = [
            "test/fixtures/templates/good/resources/s3/access-control-ownership.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/s3/access-control-ownership.yaml", 4
        )
