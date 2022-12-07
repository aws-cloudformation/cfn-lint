"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.events.RuleTargetsLimit import (
    RuleTargetsLimit,  # pylint: disable=E0401
)


class TestRuleTargetsLimit(BaseRuleTestCase):
    """Test Limits of Event Rules Targets"""

    def setUp(self):
        """Setup"""
        super(TestRuleTargetsLimit, self).setUp()
        self.collection.register(RuleTargetsLimit())
        self.success_templates = [
            "test/fixtures/templates/good/resources/events/rule_targets_limit.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/events/rule_targets_limit.yaml", 1
        )
