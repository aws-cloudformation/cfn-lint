"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.events.RuleScheduleExpression import (
    RuleScheduleExpression,  # pylint: disable=E0401
)


class TestRuleScheduleExpression(BaseRuleTestCase):
    """Test Event Rules ScheduledExpression format"""

    def setUp(self):
        """Setup"""
        super(TestRuleScheduleExpression, self).setUp()
        self.collection.register(RuleScheduleExpression())
        self.success_templates = [
            "test/fixtures/templates/good/resources/events/rule_schedule_expression.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/events/rule_schedule_expression.yaml",
            8,
        )
