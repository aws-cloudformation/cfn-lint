"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.LimitValue import LimitValue  # pylint: disable=E0401


class TestParameterLimitValue(BaseRuleTestCase):
    """Test parameters limit number"""

    def setUp(self):
        """Setup"""
        super(TestParameterLimitValue, self).setUp()
        self.collection.register(LimitValue())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/limit_parameter_value.yaml", 3
        )
