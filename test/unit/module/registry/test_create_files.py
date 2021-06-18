import logging
import six

import cfnlint.core
import cfnlint.schemaManager
from test.testlib.testcase import BaseTestCase

from mock import patch, mock_open

LOGGER = logging.getLogger('cfnlint')


class TestCreateFiles(BaseTestCase):
    """Test create schema and metadata files """

    @patch('builtins.open', new_callable=mock_open, read_data="data")
    @patch('json.dump')
    def test_create_schema_file(self, json_dump, mock_file):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        if six.PY2:
            with patch("__builtin__.open", mock_open(read_data="data")) as builtin:
                schema_manager.create_schema_file('data', 'path-test')
                builtin.assert_called_with("path-test/schema.json", "w")
        else:
            schema_manager.create_schema_file('data', 'path-test')
            mock_file.assert_called_with("path-test/schema.json", "w")

        json_dump.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data="data")
    @patch('json.dump')
    def test_create_metadata_file(self, json_dump, mock_file):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        if six.PY2:
            with patch("__builtin__.open", mock_open(read_data="data")) as builtin:
                schema_manager.create_metadata_file('data', 'path-test')
                builtin.assert_called_with("path-test/metadata.json", "w")
        else:
            schema_manager.create_metadata_file('data', 'path-test')
            mock_file.assert_called_with("path-test/metadata.json", "w")

        json_dump.assert_called_once()

    def test_create_metadata_bad_path(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        err = None
        if six.PY2:
            try:
                schema_manager.create_metadata_file('data', 'bad-path')
            except IOError as e:
                err = e
            assert (type(err) == IOError)

        else:
            try:
                schema_manager.create_metadata_file('data', 'bad-path')
            except OSError as e:
                err = e
            assert (type(err) == OSError)

    def test_create_schema_bad_path(self):
        filename = 'test/fixtures/templates/good/generic.yaml'
        (args, filenames, _) = cfnlint.core.get_args_filenames(['--template', filename])
        (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
        schema_manager = cfnlint.schemaManager.SchemaManager(filename, template, ['us-east-1'])

        err = None
        if six.PY2:
            try:
                schema_manager.create_schema_file('data', 'bad-path')
            except IOError as e:
                err = e
            assert (type(err) == IOError)

        else:
            try:
                schema_manager.create_schema_file('data', 'bad-path')
            except OSError as e:
                err = e
            assert (type(err) == OSError)
