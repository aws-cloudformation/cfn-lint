"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.RetentionPeriodOnResourceTypesWithAutoExpiringContent import (
    RetentionPeriodOnResourceTypesWithAutoExpiringContent,  # pylint: disable=E0401
)


class TestRetentionPeriodOnResourceTypesWithAutoExpiringContent(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestRetentionPeriodOnResourceTypesWithAutoExpiringContent, self).setUp()
        self.collection.register(
            RetentionPeriodOnResourceTypesWithAutoExpiringContent()
        )
        self.success_templates = [
            "test/fixtures/templates/good/resources/sqs/retention_period.yaml",
            "test/fixtures/templates/good/resources/rds/retention_period.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/sqs/retention_period.yaml", 3
        )

    def test_file_negative_rds(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/rds/retention_period.yaml", 1
        )
