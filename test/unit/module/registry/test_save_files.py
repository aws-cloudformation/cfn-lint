import logging

import cfnlint.core
import cfnlint.schema_manager
from test.testlib.testcase import BaseTestCase

from mock import patch

LOGGER = logging.getLogger('cfnlint')


class TestSaveFiles(BaseTestCase):
    """Test save files """

    @patch('cfnlint.schema_manager.SchemaManager.create_schema_file')
    @patch('cfnlint.schema_manager.SchemaManager.create_metadata_file')
    def test_create_schema_file(self, metadata, schema):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schema_manager.SchemaManager(['us-east-1'])

        response = {'Metadata': 'Metadata', 'Schema': 'Schema'}
        schema_manager.save_files(response, 'path-test')

        metadata.assert_called_with({'Metadata': 'Metadata'}, 'path-test')
        schema.assert_called_with({'Schema': 'Schema'}, 'path-test')


