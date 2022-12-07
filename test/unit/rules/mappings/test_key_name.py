"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.mappings.KeyName import KeyName  # pylint: disable=E0401


class TestKeyName(BaseRuleTestCase):
    """Test template Condition Names"""

    def setUp(self):
        """Setup"""
        super(TestKeyName, self).setUp()
        self.collection.register(KeyName())
        self.success_templates = ["test/fixtures/templates/good/mappings/key_name.yaml"]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/mappings/key_name.yaml", 4
        )
