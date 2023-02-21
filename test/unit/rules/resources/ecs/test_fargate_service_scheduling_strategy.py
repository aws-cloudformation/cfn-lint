"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.ecs.FargateDeploymentSchedulingStrategy import (
    FargateDeploymentSchedulingStrategy,
)


class TestFargateServiceSchedulingStrategy(BaseRuleTestCase):
    """
    Test that Fargate service has correct scheduling strategy (REPLICA)
    """

    def setUp(self):
        super(TestFargateServiceSchedulingStrategy, self).setUp()
        self.collection.register(FargateDeploymentSchedulingStrategy())
        self.success_templates = [
            "test/fixtures/templates/good/resources/ecs/test_fargate_scheduling_strategy.yaml"
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/ecs/test_fargate_scheduling_strategy.yaml",
            1,
        )
