"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.ecs.TaskDefinitionEssentialContainer import (
    TaskDefinitionEssentialContainer,  # pylint: disable=E0401
)


class TestECSTaskDefinitionEssentialContainer(BaseRuleTestCase):
    """Test ECS Task Definition has at least one essential container defined"""

    def setUp(self):
        """Setup"""
        super(TestECSTaskDefinitionEssentialContainer, self).setUp()
        self.collection.register(TaskDefinitionEssentialContainer())
        self.success_templates = [
            "test/fixtures/templates/good/resources/ecs/test_ecs_task_definition_essential_container.yml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/ecs/test_ecs_task_definition_essential_container.yml",
            1,
        )
