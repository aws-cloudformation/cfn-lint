import logging

import cfnlint.core
import cfnlint.schema_manager
from cfnlint.helpers import MODULE_SCHEMAS
from test.testlib.testcase import BaseTestCase

from botocore.stub import Stubber
import boto3
from mock import patch

LOGGER = logging.getLogger('cfnlint')


class TestCreateFolder(BaseTestCase):
    """Test Create Folder """

    @patch('cfnlint.schema_manager.SchemaManager.save_files')
    @patch('os.makedirs')
    @patch('cfnlint.schema_manager.SchemaManager.aws_call_registry')
    def test_create_folder(self, aws_call, makedirs, save_files):

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client

        aws_call.return_value = 'RESPONSE'
        schema_manager.create_folder('/test-path', 'module_id', 'TEST', 'MODULE', False)
        save_files.assert_called_with('RESPONSE', '/test-path')
        MODULE_SCHEMAS.remove('/test-path')

    @patch('cfnlint.schema_manager.SchemaManager.aws_call_registry')
    def test_create_folder_already_existing(self, aws_call):

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])
        aws_call.return_value = 'RESPONSE'
        err = None
        try:
            schema_manager.create_folder('/', 'module_id', 'TEST', 'MODULE', False)
        except OSError as e:
            err = e
        assert (type(err) == OSError)
        MODULE_SCHEMAS.remove('/')

    @patch('cfnlint.schema_manager.SchemaManager.save_files')
    @patch('os.makedirs')
    @patch('cfnlint.schema_manager.SchemaManager.aws_call_registry')
    def test_no_create_folder(self, aws_call, makedirs, save_files):

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])

        aws_call.return_value = None
        schema_manager.create_folder('/test-path', 'module_id', 'TEST', 'MODULE', False)
        save_files.assert_not_called()
        makedirs.assert_not_called()
