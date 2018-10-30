"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import logging
from mock import patch, mock_open
import cfnlint.config  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


LOGGER = logging.getLogger('cfnlint')


class TestConfigFileArgs(BaseTestCase):
    """Test ConfigParser Arguments """
    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch('cfnlint.config.ConfigParser')
    def test_config_parser_read(self, config_parser_class_mock):
        """ test the read call to the config parser is reading two files """
        config_parser_mock = config_parser_class_mock.return_value
        cfnlint.config.ConfigFileArgs()

        config_parser_class_mock.assert_called_once_with()
        config_parser_mock.read.assert_called_once_with(['~/.cfnlint', '.cfnlint'])

    @patch('cfnlint.config.ConfigParser.sections')
    @patch('cfnlint.config.ConfigParser.items')
    def test_config_file_convert_list(self, mock_items, mock_sections):
        """ Test conversions between string, comma lists into arrays """
        mock_sections.return_value = {'Defaults'}
        mock_items.return_value = {'include_checks': 'I,I1111', 'templates': 'test.yaml'}
        config = cfnlint.config.ConfigFileArgs()
        self.assertEqual(config.file_args, {'include_checks': ['I', 'I1111'], 'templates': ['test.yaml']})
