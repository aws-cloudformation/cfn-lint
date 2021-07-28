import logging

import cfnlint.core
import cfnlint.schema_manager
from test.testlib.testcase import BaseTestCase

from mock import patch, MagicMock

LOGGER = logging.getLogger('cfnlint')


class TestCreatePath(BaseTestCase):
    """Test Create Path """

    def test_create_path(self):
        """Create path (mac/linux)"""
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(filename, template, ['us-east-1'])
        with patch("os.path.join",
                   MagicMock(return_value='/Users/username/.cloudformation/account_id/region/name')):
            assert schema_manager.create_path('account_id', 'region', 'name') == \
               '/Users/username/.cloudformation/account_id/region/name'
