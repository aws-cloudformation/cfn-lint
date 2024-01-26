"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.Modules import Modules


class TestModules(BaseRuleTestCase):
    def setUp(self):
        """Setup"""
        super(TestModules, self).setUp()
        self.collection.register(Modules())
        self.success_templates = [
            "test/fixtures/templates/good/modules/minimal.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_cannot_have_update_policy(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/modules/bad_has_update_policy.yaml", 1
        )

    def test_cannot_have_create_policy(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/modules/bad_has_create_policy.yaml", 1
        )

    def test_cannot_use_special_metadata_keyword(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/modules/bad_uses_module_metadata.yaml", 1
        )

    def test_cannot_use_tags(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/modules/bad_has_tags.yaml", 1
        )
