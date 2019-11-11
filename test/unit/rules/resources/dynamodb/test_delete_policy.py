"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.dynamodb.TableDeletionPolicy import TableDeletionPolicy  # pylint: disable=E0401


class TestTableDeletionPolicy(BaseRuleTestCase):
    """Test StateMachine for Step Functions"""

    def setUp(self):
        """Setup"""
        super(TestTableDeletionPolicy, self).setUp()
        self.collection.register(TableDeletionPolicy())
        self.success_templates = [
            'test/fixtures/templates/good/resources/dynamodb/delete_policy.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/dynamodb/delete_policy.yaml', 1)
