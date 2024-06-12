"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import datetime
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.DeprecatedRuntimeUpdate import DeprecatedRuntimeUpdate


class TestDeprecatedRuntimeUpdate(BaseRuleTestCase):
    """Test Lambda Deprecated Runtime usage"""

    def setUp(self):
        """Setup"""
        super(TestDeprecatedRuntimeUpdate, self).setUp()
        rule = DeprecatedRuntimeUpdate()
        self.collection.register(rule)
        self.collection.rules[rule.id].current_date = datetime(2021, 8, 30)

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/runtimes.yaml", 2
        )
