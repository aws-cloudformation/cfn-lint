import logging
import six

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

from mock import patch, mock_open

LOGGER = logging.getLogger('cfnlint')


class TestGetLocalVersionId(BaseTestCase):
    """Test get local version id """

    def test_get_local_version_id(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(['us-east-1'])

        if six.PY2:
            with patch("__builtin__.open", mock_open(read_data='{\"DefaultVersionId\": \"000001\"}')) as builtin:
                assert schema_manager.get_local_version_id('path') == '000001'
        else:
            with patch("builtins.open", mock_open(read_data='{\"DefaultVersionId\": \"000001\"}')) as builtin:
                assert schema_manager.get_local_version_id('path') == '000001'

