"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.dynamodb.BillingMode import BillingMode  # pylint: disable=E0401


class TestBillingMode(BaseRuleTestCase):
    """Test BillingMode"""

    def setUp(self):
        """Setup"""
        super(TestBillingMode, self).setUp()
        self.collection.register(BillingMode())
        self.success_templates = [
            'test/fixtures/templates/good/resources/dynamodb/billing_mode.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/dynamodb/billing_mode.yaml', 3)
