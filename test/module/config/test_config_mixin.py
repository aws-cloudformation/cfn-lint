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
    def test_config_expand_paths(self, yaml_mock):
        """ Test precedence in  """

        yaml_mock.side_effect = [
            {'templates': ['fixtures/templates/public/*.yaml']},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.templates, [
            'fixtures/templates/public/lambda-poller.yaml',
            'fixtures/templates/public/rds-cluster.yaml'])

    @patch('cfnlint.config.ConfigFileArgs._read_config', create=True)
    def test_config_expand_paths_failure(self, yaml_mock):
        """ Test precedence in  """

        yaml_mock.side_effect = [
            {'templates': ['*.yaml']},
            {}
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.templates, ['*.yaml'])
