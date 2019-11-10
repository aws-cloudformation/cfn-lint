"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from test.testlib.testcase import BaseTestCase
from mock import patch
import cfnlint.config  # pylint: disable=E0401
from cfnlint.helpers import REGIONS


LOGGER = logging.getLogger('cfnlint')


class TestConfigMixIn(BaseTestCase):
    """Test ConfigParser Arguments """

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_mix_in(self, yaml_mock):
        """ Test mix in  """
        yaml_mock.side_effect = [
            {"include_checks": ["I", "I1111"], "regions": ["us-west-2"]},
            {}
        ]

        config = cfnlint.config.ConfigMixIn(['--regions', 'us-west-1'])
        self.assertEqual(config.regions, ['us-west-1'])
        self.assertEqual(config.include_checks, ['I', 'I1111'])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_precedence(self, yaml_mock):
        """ Test precedence in  """

        yaml_mock.side_effect = [
            {"include_checks": ["I"], "ignore_checks": ["E3001"], "regions": ["us-west-2"]},
            {}
        ]
        config = cfnlint.config.ConfigMixIn(['--include-checks', 'I1234', 'I4321'])
        config.template_args = {
            'Metadata': {
                'cfn-lint': {
                    'config': {
                        'include_checks': ['I9876'],
                        'ignore_checks': ['W3001']
                    }
                }
            }
        }
        # config files wins
        self.assertEqual(config.regions, ['us-west-2'])
        # CLI should win
        self.assertEqual(config.include_checks, ['I1234', 'I4321'])
        # template file wins over config file
        self.assertEqual(config.ignore_checks, ['W3001'])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_default_region(self, yaml_mock):
        """ Test precedence in  """

        yaml_mock.side_effect = [
            {},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ['us-east-1'])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_all_regions(self, yaml_mock):
        """ Test precedence in """

        yaml_mock.side_effect = [
            {'regions': ['ALL_REGIONS']},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, REGIONS)

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_expand_paths(self, yaml_mock):
        """ Test precedence in  """

        yaml_mock.side_effect = [
            {'templates': ['test/fixtures/templates/public/*.yaml']},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.templates, [
            'test/fixtures/templates/public/lambda-poller.yaml',
            'test/fixtures/templates/public/rds-cluster.yaml'])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_expand_paths_failure(self, yaml_mock):
        """ Test precedence in  """

        yaml_mock.side_effect = [
            {'templates': ['test/fixtures/templates/badpath/*.yaml']},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.templates, ['test/fixtures/templates/badpath/*.yaml'])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_expand_ignore_templates(self, yaml_mock):
        """ Test ignore templates """

        yaml_mock.side_effect = [
            {
                'templates': ['test/fixtures/templates/bad/resources/iam/*.yaml'],
                'ignore_templates': ['test/fixtures/templates/bad/resources/iam/resource_*.yaml']},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertNotIn(
            'test/fixtures/templates/bad/resources/iam/resource_policy.yaml', config.templates)
        self.assertEqual(len(config.templates), 4)
