"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from test.testlib.testcase import BaseTestCase
import jsonschema
from mock import patch
import cfnlint.config  # pylint: disable=E0401
LOGGER = logging.getLogger('cfnlint')


class TestCli(BaseTestCase):
    """Test CLI processing """

    def tearDown(self):
        """ Tear Down """
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_template_not_found(self):
        """Test template not found"""

        filename = 'test/fixtures/templates/good/core/not_found.yaml'

        linter = cfnlint.Linter()
        linter.config.templates = [filename]
        linter.lint()

        self.assertEqual(len(linter.matches), 1)

    def test_template_invalid_yaml(self):
        """Test template invalid yaml"""
        filename = 'test/fixtures/templates/bad/core/config_invalid_yaml.yaml'

        linter = cfnlint.Linter()
        linter.config.templates = [filename]
        linter.lint()

        self.assertEqual(len(linter.matches), 1)

    def test_template_invalid_json(self):
        """Test template not found"""

        filename = 'test/fixtures/templates/bad/core/config_invalid_json.json'

        linter = cfnlint.Linter()
        linter.config.templates = [filename]
        linter.lint()

        self.assertEqual(len(linter.matches), 1)

    def test_template_invalid_yaml_ignore(self):
        """Test template not found"""
        filename = 'test/fixtures/templates/bad/core/config_invalid_yaml.yaml'

        linter = cfnlint.Linter()
        linter.config.templates = [filename]
        linter.lint()

        self.assertEqual(len(linter.matches), 1)

    def test_template_invalid_json_ignore(self):
        """Test template not found"""
        filename = 'test/fixtures/templates/bad/core/config_invalid_json.json'

        linter = cfnlint.Linter()
        linter.config.templates = [filename]
        linter.lint()

        self.assertEqual(len(linter.matches), 1)

    @patch('cfnlint.config.ConfigMixIn', create=True)
    def test_get_config_failure(self, config_mock):
        """ Test linter with validation error """

        config_mock.side_effect = jsonschema.exceptions.ValidationError('fail')
        with self.assertRaises(cfnlint.InvalidConfiguation):
            cfnlint.Linter()

    @patch('cfnlint.rules.RulesCollection.create_from_directory', create=True)
    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_get_formatter_parseable(self, yaml_mock, create_mock):
        """ Test get rules failure """

        yaml_mock.side_effect = [
            {},
            {}
        ]

        linter = cfnlint.Linter()

        create_mock.side_effect = OSError('fail')
        with self.assertRaises(cfnlint.UnexpectedRuleException):
            linter.get_rules('dir', [], [])
