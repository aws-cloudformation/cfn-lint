"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.stepfunctions.StateMachine import (
    StateMachine,  # pylint: disable=E0401
)


class TestStateMachine(BaseRuleTestCase):
    """Test StateMachine for Step Functions"""

    def setUp(self):
        """Setup"""
        super(TestStateMachine, self).setUp()
        self.collection.register(StateMachine())
        self.success_templates = [
            "test/fixtures/templates/good/resources/stepfunctions/state_machine.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/stepfunctions/state_machine.yaml", 5
        )
