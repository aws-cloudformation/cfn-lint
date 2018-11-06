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
from mock import patch, mock_open, Mock
import jsonschema
import cfnlint.config  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


LOGGER = logging.getLogger('cfnlint')


class TestConfigFileArgs(BaseTestCase):
    """Test ConfigParser Arguments """
    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_parser_read(self, yaml_mock):
        """ Testing one file successful """
        # cfnlintrc_mock.return_value.side_effect = [Mock(return_value=True), Mock(return_value=False)]
        yaml_mock.side_effect = [
            {"regions": ["us-west-1"]},
            {}
        ]
        results = cfnlint.config.ConfigFileArgs()
        self.assertEqual(results.file_args, {'regions': ['us-west-1']})

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_parser_read_merge(self, yaml_mock):
        """ test the merge of config """

        yaml_mock.side_effect = [
            {"regions": ["us-west-1"]},
            {"regions": ["us-east-1"]}
        ]

        results = cfnlint.config.ConfigFileArgs()
        self.assertEqual(results.file_args, {'regions': ['us-east-1']})

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_parser_fail_on_bad_config(self, yaml_mock):
        """ test the read call to the config parser is reading two files """

        yaml_mock.side_effect = [
            {"regions": True}, {}
        ]

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            cfnlint.config.ConfigFileArgs()
