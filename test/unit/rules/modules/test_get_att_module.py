"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
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
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        path = os.path.join(fileDir, 'test', 'fixtures', 'templates', 'bad', 'modules', 'us-east-1',
                            'Some--IAM--Role--MODULE')
        MODULE_SCHEMAS.append(path)
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_attribute.yaml', 1)
        MODULE_SCHEMAS.remove(path)

    def test_file_negative_resource(self):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        path = os.path.join(fileDir, 'test', 'fixtures', 'templates', 'bad', 'modules', 'us-east-1',
                            'Some--IAM--Role--MODULE')
        MODULE_SCHEMAS.append(path)
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_resource.yaml', 1)
        MODULE_SCHEMAS.remove(path)

    def test_file_negative_resource_type(self):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        path = os.path.join(fileDir, 'test', 'fixtures', 'templates', 'bad', 'modules', 'us-east-1',
                            'Some--IAM--Role--MODULE')
        MODULE_SCHEMAS.append(path)
        del RESOURCE_SPECS['us-east-1'].get('ResourceTypes')['AWS::S3::Bucket']
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_resource_type.yaml', 1)
        RESOURCE_SPECS.clear()
        cfnlint.helpers.initialize_specs()
        MODULE_SCHEMAS.remove(path)

    def test_file_negative_resource_no_attributes(self):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        path = os.path.join(fileDir, 'test', 'fixtures', 'templates', 'bad', 'modules', 'us-east-1',
                            'Some--IAM--Role--MODULE')
        MODULE_SCHEMAS.append(path)
        del RESOURCE_SPECS['us-east-1'].get('ResourceTypes')['AWS::S3::Bucket']['Attributes']
        self.helper_file_negative('test/fixtures/templates/bad/modules/bad_invalid_get_att_resource_type.yaml', 1)
        RESOURCE_SPECS.clear()
        cfnlint.helpers.initialize_specs()
        MODULE_SCHEMAS.remove(path)


