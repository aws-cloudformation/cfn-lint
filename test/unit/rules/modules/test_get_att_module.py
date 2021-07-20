"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import cfnlint.helpers
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.modules.GettAttModule import GetAttModule
from cfnlint.helpers import MODULE_SCHEMAS, RESOURCE_SPECS


class TestGetAttModule(BaseRuleTestCase):

    def setUp(self):
        """Setup"""
        super(TestGetAttModule, self).setUp()
        self.collection.validate_registry_types = ['MODULE']
        self.collection.register(GetAttModule())
        self.success_templates = [
            'test/fixtures/templates/good/modules/minimal.yaml',
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_attribute(self):
        MODULE_SCHEMAS.clear()
        MODULE_SCHEMAS.append('test/fixtures/templates/bad/modules/us-east-1/Some::IAM::Role::MODULE')
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_attribute.yaml', 1)

    def test_file_negative_resource(self):
        MODULE_SCHEMAS.clear()
        MODULE_SCHEMAS.append('test/fixtures/templates/bad/modules/us-east-1/Some::IAM::Role::MODULE')
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_resource.yaml', 1)

    def test_file_negative_resource_type(self):
        MODULE_SCHEMAS.clear()
        MODULE_SCHEMAS.append('test/fixtures/templates/bad/modules/us-east-1/Some::IAM::Role::MODULE')
        del RESOURCE_SPECS['us-east-1'].get('ResourceTypes')['AWS::S3::Bucket']
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_resource_type.yaml', 1)
        RESOURCE_SPECS.clear()
        cfnlint.helpers.initialize_specs()

    def test_file_negative_resource_no_attributes(self):
        MODULE_SCHEMAS.clear()
        MODULE_SCHEMAS.append('test/fixtures/templates/bad/modules/us-east-1/Some::IAM::Role::MODULE')
        del RESOURCE_SPECS['us-east-1'].get('ResourceTypes')['AWS::S3::Bucket']['Attributes']
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_resource_type.yaml', 1)
        RESOURCE_SPECS.clear()
        cfnlint.helpers.initialize_specs()

