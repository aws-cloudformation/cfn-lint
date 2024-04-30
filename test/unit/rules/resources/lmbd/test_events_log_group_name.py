"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.EventsLogGroupName import EventsLogGroupName


class TestEventsLogGroupName(BaseRuleTestCase):
    """Test Lambda Trigger Events CloudWatchLogs Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestEventsLogGroupName, self).setUp()
        self.collection.register(EventsLogGroupName())
        self.success_templates = [
            "test/fixtures/templates/good/some_logs_stream_lambda.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/some_logs_stream_lambda.yaml", 1
        )
