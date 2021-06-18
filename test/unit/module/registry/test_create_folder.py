import logging

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

from mock import patch

LOGGER = logging.getLogger('cfnlint')


class TestCreateFolder(BaseTestCase):
    """Test Create Folder """

    @patch('cfnlint.schemaManager.SchemaManager.save_files')
    @patch('os.makedirs')
    @patch('cfnlint.schemaManager.SchemaManager.aws_call_registry')
    def test_create_folder(self, aws_call, makedirs, save_files):

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        aws_call.return_value = 'RESPONSE'
        schema_manager.create_folder('/test-path', 'TEST', 'MODULE')
        save_files.assert_called_with('RESPONSE', '/test-path')

    @patch('cfnlint.schemaManager.SchemaManager.aws_call_registry')
    def test_create_folder_already_existing(self, aws_call):

        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])
        err = None
        try:
            schema_manager.create_folder('/', 'TEST', 'MODULE')
        except OSError as e:
            err = e
        assert (type(err) == OSError)
