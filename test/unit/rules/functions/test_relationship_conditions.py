"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.RelationshipConditions import (
    RelationshipConditions,  # pylint: disable=E0401
)


class TestRulesRelationshipConditions(BaseRuleTestCase):
    """Test Rules Ref exists"""

    def setUp(self):
        """Setup"""
        super(TestRulesRelationshipConditions, self).setUp()
        self.collection.register(RelationshipConditions())
        self.success_templates = [
            "test/fixtures/templates/good/functions/relationship_conditions.yaml",
            "test/fixtures/templates/good/functions/relationship_conditions_sam.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/relationship_conditions.yaml", 5
        )
