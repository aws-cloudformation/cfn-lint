"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import jsonschema

import cfnlint.config  # pylint: disable=E0401

LOGGER = logging.getLogger("cfnlint")


class TestConfigFileArgs(BaseTestCase):
    """Test ConfigParser Arguments"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_config_parser_read_config(self):
        """Testing one file successful"""
        config = cfnlint.config.ConfigFileArgs(
            config_file=Path("test/fixtures/configs/cfnlintrc_read.yaml")
        )
        self.assertEqual(
            config.file_args,
            {
                "templates": ["test/fixtures/templates/good/**/*.yaml"],
                "include_checks": ["I"],
            },
        )

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_parser_read_config_only_one_read(self, yaml_mock):
        """Testing one file successful"""
        # Should only have one read here
        # We aren't going to search and find the possible locations of
        # cfnlintrc
        yaml_mock.side_effect = [
            {"regions": ["us-west-1"]},
        ]
        config = cfnlint.config.ConfigFileArgs(
            config_file=Path("test/fixtures/configs/cfnlintrc_read.yaml")
        )
        self.assertEqual(config.file_args, {"regions": ["us-west-1"]})

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_parser_read(self, yaml_mock):
        """Testing one file successful"""
        yaml_mock.side_effect = [{"regions": ["us-west-1"]}, {}]
        results = cfnlint.config.ConfigFileArgs()
        self.assertEqual(results.file_args, {"regions": ["us-west-1"]})

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_parser_read_merge(self, yaml_mock):
        """test the merge of config"""

        yaml_mock.side_effect = [{"regions": ["us-west-1"]}, {"regions": ["us-east-1"]}]

        results = cfnlint.config.ConfigFileArgs()
        self.assertEqual(results.file_args, {"regions": ["us-east-1"]})

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_parser_fail_on_bad_config(self, yaml_mock):
        """test the read call to the config parser is reading two files"""

        yaml_mock.side_effect = [{"regions": True}, {}]

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            cfnlint.config.ConfigFileArgs()

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_parser_fail_on_config_rules(self, yaml_mock):
        """test the read call to the config parser is parsing configure rules correctly"""

        yaml_mock.side_effect = [{"configure_rules": {"E3012": {"strict": False}}}, {}]

        results = cfnlint.config.ConfigFileArgs()
        self.assertEqual(
            results.file_args, {"configure_rules": {"E3012": {"strict": False}}}
        )
