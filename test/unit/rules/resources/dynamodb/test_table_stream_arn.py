"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.dynamodb.TableStreamArn import (  # pylint: disable=E0401
    TableStreamArn,
)


class TestTableStreamArn(BaseRuleTestCase):
    """Test TableStreamArn"""

    def setUp(self):
        """Setup"""
        super(TestTableStreamArn, self).setUp()
        self.collection.register(TableStreamArn())
        self.success_templates = [
            "test/fixtures/templates/good/resources/dynamodb/table_stream_arn.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/dynamodb/table_stream_arn.yaml",
            3,
        )
