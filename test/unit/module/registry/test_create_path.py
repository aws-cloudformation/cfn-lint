import logging

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

from mock import patch, MagicMock

LOGGER = logging.getLogger('cfnlint')


class TestCreatePath(BaseTestCase):
    """Test Create Path """

    def test_create_path_windows(self):
        """Create path (windows)"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])
        with patch("os.path.join", MagicMock(return_value=r'C:\Users\username\AppData\cloudformation\account_id\region\name')):
            assert schema_manager.create_path(True, 'username', 'account_id', 'region', 'name') == \
                r'C:\Users\username\AppData\cloudformation\account_id\region\name'

    def test_create_path_mac_linux(self):
        """Create path (mac/linux)"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])
        with patch("os.path.join",
                   MagicMock(return_value='/Users/username/.cloudformation/account_id/region/name')):
            assert schema_manager.create_path(False, 'username', 'account_id', 'region', 'name') == \
               '/Users/username/.cloudformation/account_id/region/name'
