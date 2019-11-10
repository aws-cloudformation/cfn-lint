"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from test.testlib.testcase import BaseTestCase
import jsonschema
from mock import patch
import cfnlint.config  # pylint: disable=E0401
try:  # pragma: no cover
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path


LOGGER = logging.getLogger('cfnlint')


class TestConfigFileArgs(BaseTestCase):
    """Test ConfigParser Arguments """

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_config_parser_read_config(self):
        """ Testing one file successful """
        # cfnlintrc_mock.return_value.side_effect = [Mock(return_value=True), Mock(return_value=False)]
        config = cfnlint.config.ConfigFileArgs()
        config_file = Path('test/fixtures/configs/cfnlintrc_read.yaml')
        config_template = config._read_config(config_file)
        self.assertEqual(
            config_template,
            {
                'templates': ['test/fixtures/templates/good/**/*.yaml'],
                'include_checks': ['I']
            }
        )

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

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_parser_fail_on_config_rules(self, yaml_mock):
        """ test the read call to the config parser is parsing configure rules correctly"""

        yaml_mock.side_effect = [
            {
                'configure_rules': {
                    'E3012': {
                        'strict': False
                    }
                }
            }, {}
        ]

        results = cfnlint.config.ConfigFileArgs()
        self.assertEqual(results.file_args, {'configure_rules': {'E3012': {'strict': False}}})
