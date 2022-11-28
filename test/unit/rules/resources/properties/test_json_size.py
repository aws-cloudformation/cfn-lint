"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.JsonSize import (
    JsonSize,  # pylint: disable=E0401
)


class TestJsonSize(BaseRuleTestCase):
    """Test Json Size"""

    def setUp(self):
        """Setup"""
        super(TestJsonSize, self).setUp()
        self.collection.register(JsonSize())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/json_size.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_role_assume_role_policy_document(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/properties/json_size.yaml", 2
        )
