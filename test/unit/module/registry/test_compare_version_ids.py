import logging

import cfnlint.core
import cfnlint.schema_manager
from test.testlib.testcase import BaseTestCase

from botocore.stub import Stubber
import boto3
from mock import patch

LOGGER = logging.getLogger('cfnlint')


class TestCompareVersionIds(BaseTestCase):
    """Test compare version ids """

    @patch('cfnlint.schema_manager.SchemaManager.get_registry_version_id')
    @patch('cfnlint.schema_manager.SchemaManager.get_local_version_id')
    @patch('cfnlint.schema_manager.SchemaManager.create_folder')
    def test_compare_version_ids_windows_same(self, create_folder, local_version, registry_version):

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])
        schema_manager.is_windows = True
        schema_manager.username = 'username'

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client

        local_version.return_value = '00001'
        registry_version.return_value = ('00001', 'MODULE')

        with patch('os.listdir', return_value=['AWS::TEST::MODULE']):
            schema_manager.compare_version_ids(False, '/', 'TEST', 'module_id')
        create_folder.assert_not_called()

    @patch('cfnlint.schema_manager.SchemaManager.get_registry_version_id')
    @patch('cfnlint.schema_manager.SchemaManager.get_local_version_id')
    @patch('cfnlint.schema_manager.SchemaManager.create_folder')
    def test_compare_version_ids_is_update(self, create_folder, local_version, registry_version):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])
        schema_manager.is_windows = False
        schema_manager.username = 'username'

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client

        local_version.return_value = '00001'
        registry_version.return_value = ('00002', 'MODULE')

        with patch('os.listdir', return_value=['AWS::TEST::MODULE']):
            schema_manager.compare_version_ids(True, '/', 'AWS::TEST::MODULE', 'module_id')
        create_folder.assert_called_with('/', 'module_id', 'AWS::TEST::MODULE', 'MODULE', True)

    @patch('cfnlint.schema_manager.SchemaManager.get_registry_version_id')
    @patch('cfnlint.schema_manager.SchemaManager.get_local_version_id')
    @patch('cfnlint.schema_manager.SchemaManager.create_folder')
    def test_compare_version_ids_is_update_same(self, create_folder, local_version, registry_version):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])
        schema_manager.is_windows = False
        schema_manager.username = 'username'

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client

        local_version.return_value = '00001'
        registry_version.return_value = ('00001', 'MODULE')

        with patch('os.listdir', return_value=['AWS::TEST::MODULE']):
            schema_manager.compare_version_ids(True, '/', 'TEST', 'module_id')
        create_folder.assert_not_called()
