"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.modules.ModuleInRegistry import ModuleInRegistry  # pylint: disable=E0401
from cfnlint.helpers import INVALID_MODULES


class TestModuleInRegistry(BaseRuleTestCase):
    """Test Module updated"""

    def setUp(self):
        """Setup"""
        super(TestModuleInRegistry, self).setUp()
        self.collection.register(ModuleInRegistry())
        self.success_templates = [
            'test/fixtures/templates/good/modules/minimal.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        INVALID_MODULES['MODULE'] = 'My::Organization::Custom::MODULE'
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_not_updated.yaml', 1)
        INVALID_MODULES.clear()
