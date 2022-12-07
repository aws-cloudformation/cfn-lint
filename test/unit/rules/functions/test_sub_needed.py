"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.SubNeeded import SubNeeded  # pylint: disable=E0401


class TestSubNeeded(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestSubNeeded, self).setUp()
        self.collection.register(SubNeeded())
        self.success_templates = [
            "test/fixtures/templates/good/functions/sub.yaml",
            "test/fixtures/templates/good/functions/sub_needed.yaml",
            "test/fixtures/templates/good/functions/sub_needed_transform.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_template_config(self):
        """Test custom excludes configuration"""
        self.helper_file_rule_config(
            "test/fixtures/templates/good/functions/sub_needed_custom_excludes.yaml",
            {"custom_excludes": "^\\$\\{Stage\\}$"},
            0,
        )
        self.helper_file_rule_config(
            "test/fixtures/templates/good/functions/sub_needed_custom_excludes.yaml",
            {},
            1,
        )

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/sub_needed.yaml", 7
        )
