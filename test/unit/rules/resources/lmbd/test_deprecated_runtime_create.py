"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import datetime
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.DeprecatedRuntimeCreate import DeprecatedRuntimeCreate


class TestDeprecatedRuntimeCreate(BaseRuleTestCase):
    """Test Lambda Deprecated Runtime usage"""

    def setUp(self):
        """Setup"""
        super(TestDeprecatedRuntimeCreate, self).setUp()
        rule = DeprecatedRuntimeCreate()
        self.collection.register(rule)
        self.collection.rules[rule.id].current_date = datetime(2021, 8, 30)

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/runtimes.yaml", 1
        )


class TestDeprecatedRuntimeCreateMatchDate(BaseRuleTestCase):
    """Test Lambda Deprecated Runtime usage"""

    def setUp(self):
        """Setup"""
        super(TestDeprecatedRuntimeCreateMatchDate, self).setUp()
        rule = DeprecatedRuntimeCreate()
        self.collection.register(rule)
        self.collection.rules[rule.id].current_date = datetime(2016, 10, 31)

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/runtimes.yaml", 0
        )
