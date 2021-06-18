import logging

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

from botocore.stub import Stubber
import boto3
from mock import patch

LOGGER = logging.getLogger('cfnlint')


class TestCheckFolders(BaseTestCase):
    """Test Check Folders """

    @patch('cfnlint.schemaManager.SchemaManager.create_path')
    @patch('cfnlint.schemaManager.SchemaManager.create_folder')
    @patch('os.getcwd')
    # mock the call against cloudformation registry
    def test_check_folder_existing(self, getcwd, create_folder, create_path):
        """Test folder doesn't exist (mac/linux)"""
        getcwd.return_value = 'Users/test_user'
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client
        create_path.return_value = 'new_path'
        schema_manager.check_folders('TEST', 'MODULE')
        create_folder.assert_called_with('new_path', 'TEST', 'MODULE')

    @patch('cfnlint.schemaManager.SchemaManager.create_path')
    @patch('cfnlint.schemaManager.SchemaManager.create_folder')
    @patch('os.getcwd')
    @patch('platform.system')
    def test_check_folder_existing_windows(self, system, getcwd, create_folder, create_path):
        """Test folder doesnt' exist (windows)"""
        getcwd.return_value = 'Users/test_user'
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client
        system.return_value = 'win32'
        create_path.return_value = 'new_path'
        schema_manager.check_folders('TEST', 'MODULE')
        create_folder.assert_called_with('new_path', 'TEST', 'MODULE')


    @patch('os.getcwd')
    def test_check_folder_bad_path(self, getcwd):
        """Test folder has a bad path"""
        getcwd.return_value = '/'
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client
        err = None
        try:
            schema_manager.check_folders('TEST', 'MODULE')
        except ValueError as e:
            err = e
        assert(type(err) == ValueError)
