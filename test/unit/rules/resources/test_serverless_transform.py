"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.ServerlessTransform import (
    ServerlessTransform,  # pylint: disable=E0401
)


class TestServerlessTransform(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestServerlessTransform, self).setUp()
        self.collection.register(ServerlessTransform())
        self.success_templates = [
            "test/fixtures/templates/good/generic.yaml",
            "test/fixtures/templates/good/transform_serverless_function.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/transform_serverless_missing.yaml", 1
        )
