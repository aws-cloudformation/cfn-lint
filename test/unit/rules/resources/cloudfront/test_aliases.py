"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.cloudfront.Aliases import Aliases


class TestCloudFrontAliases(BaseRuleTestCase):
    """Test CloudFront Aliases Configuration"""

    def setUp(self):
        """Setup"""
        super(TestCloudFrontAliases, self).setUp()
        self.collection.register(Aliases())
        self.success_templates = [
            "test/fixtures/templates/good/resources/cloudfront/aliases.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources_cloudfront_invalid_aliases.yaml", 8
        )
