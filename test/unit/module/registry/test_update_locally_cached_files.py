import logging

import cfnlint.core
import cfnlint.schema_manager
from test.testlib.testcase import BaseTestCase

from botocore.stub import Stubber
import boto3
from mock import patch, MagicMock

LOGGER = logging.getLogger('cfnlint')


class TestUpdateLocallyCachedFiles(BaseTestCase):
    """Test update locally cached files """

    @patch('cfnlint.schema_manager.SchemaManager.compare_version_ids')
    def test_create_schema_file(self, compare_version_ids):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])

        stubbed_client = boto3.client('sts')
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_caller_identity", {"Account": "000000000000"})
        stubber.activate()
        schema_manager.boto3_sts = stubbed_client

        with patch("os.path.join",
                   MagicMock(return_value='path')):
            with patch('os.path.expanduser') as expanduser:
                with patch('os.listdir') as mocked_listdir:
                    expanduser.return_value = 'user'
                    mocked_listdir.return_value = ['module']
                    schema_manager.update_locally_cached_schemas()
                    compare_version_ids.assert_called_with(True, 'path', 'module')
