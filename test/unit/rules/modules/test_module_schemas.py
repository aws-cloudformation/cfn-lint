"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.modules.ModuleSchema import ModuleSchema
from cfnlint.helpers import MODULE_SCHEMAS


class TestModuleSchemas(BaseRuleTestCase):

    def setUp(self):
        """Setup"""
        super(TestModuleSchemas, self).setUp()
        self.collection.validate_registry_types = ['MODULE']
        self.collection.register(ModuleSchema())
        self.success_templates = [
            'test/fixtures/templates/good/modules/minimal.yaml',
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        MODULE_SCHEMAS.append('test/fixtures/templates/bad/modules/us-east-1/Some::IAM::Role::MODULE')
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_schema.yaml', 1)
