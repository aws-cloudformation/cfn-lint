"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.modules.ModuleUpdated import ModuleUpdated  # pylint: disable=E0401
from cfnlint.helpers import MODULES_TO_UPDATE


class TestModuleUpdated(BaseRuleTestCase):
    """Test Module updated"""
    def setUp(self):
        """Setup"""
        super(TestModuleUpdated, self).setUp()
        self.collection.validate_registry_types = ['MODULE']
        self.collection.register(ModuleUpdated())
        self.success_templates = [
            'test/fixtures/templates/good/modules/minimal.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        MODULES_TO_UPDATE.append('My::Organization::Custom::MODULE')
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_not_updated.yaml', 1)
        MODULES_TO_UPDATE.remove('My::Organization::Custom::MODULE')
