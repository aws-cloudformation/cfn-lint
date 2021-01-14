"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging
import zipfile
from test.testlib.testcase import BaseTestCase
from mock import patch, MagicMock, Mock
import cfnlint.maintenance
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen

LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())


class TestUpdateResourceSpecs(BaseTestCase):
    """Used for Testing Resource Specs"""
    @patch('cfnlint.maintenance.url_has_newer_version')
    @patch('cfnlint.maintenance.get_url_content')
    @patch('cfnlint.maintenance.json.dump')
    @patch('cfnlint.maintenance.patch_spec')
    @patch('cfnlint.maintenance.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    @patch('cfnlint.maintenance.urlopen')
    def test_update_resource_spec(self, mock_urlopen, mock_patch_spec, mock_json_dump, mock_content, mock_url_newer_version):
        """Success update resource spec"""

        mock_url_newer_version.return_value = True
        mock_content.return_value = '{"PropertyTypes": {}, "ResourceTypes": {}}'
        mock_patch_spec.side_effect = [
            {
                'PropertyTypes': {},
                'ResourceTypes': {},
                'ValueTypes': {}
            },
            {
                'PropertyTypes': {},
                'ResourceTypes': {},
                'ValueTypes': {
                    'AWS::EC2::Instance.Types': [
                        'm2.medium'],
                }
            },
        ]

        mock_urlresponse = Mock()
        with open("test/fixtures/registry/schema.zip", 'rb') as f:
            byte = f.read()
            mock_urlresponse.read.side_effect = [byte]
            mock_urlopen.return_value = mock_urlresponse

        if sys.version_info.major == 3:
            builtin_module_name = 'builtins'
        else:
            builtin_module_name = '__builtin__'

        with patch('{}.open'.format(builtin_module_name)) as mock_builtin_open:
            cfnlint.maintenance.update_resource_spec('us-east-1', 'http://foo.badurl')
            mock_json_dump.assert_called_with(
                {
                    'PropertyTypes': {},
                    'ResourceTypes': {},
                    'ValueTypes': {
                        'AWS::EC2::Instance.Types': [
                            'm2.medium'
                        ],
                        'AWS::Lambda::CodeSigningConfig.AllowedPublishers.SigningProfileVersionArns': {
                            'AllowedPatternRegex': 'arn:(aws[a-zA-Z0-9-]*):([a-zA-Z0-9\\-])+:([a-z]{2}(-gov)?-[a-z]+-\\d{1})?:(\\d{12})?:(.*)',
                            'StringMin': 12,
                            'StringMax': 1024
                        },
                        'AWS::Lambda::CodeSigningConfig.CodeSigningPolicies.UntrustedArtifactOnDeployment': {
                            'AllowedValues': ['Warn', 'Enforce']
                        },
                        'AWS::Lambda::CodeSigningConfig.CodeSigningConfigId': {
                            'AllowedPatternRegex': 'csc-[a-zA-Z0-9-_\\.]{17}'
                        },
                        'AWS::Lambda::CodeSigningConfig.CodeSigningConfigArn': {
                            'AllowedPatternRegex': 'arn:(aws[a-zA-Z-]*)?:lambda:[a-z]{2}((-gov)|(-iso(b?)))?-[a-z]+-\\d{1}:\\d{12}:code-signing-config:csc-[a-z0-9]{17}'
                        }
                    }
                },
                mock_builtin_open.return_value.__enter__.return_value,
                indent=2,
                separators=(',', ': '),
                sort_keys=True
            )

    @patch('cfnlint.maintenance.url_has_newer_version')
    @patch('cfnlint.maintenance.get_url_content')
    @patch('cfnlint.maintenance.json.dump')
    @patch('cfnlint.maintenance.patch_spec')
    @patch('cfnlint.maintenance.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_do_not_update_resource_spec(self, mock_patch_spec, mock_json_dump, mock_content, mock_url_newer_version):
        """Success update resource spec"""

        mock_url_newer_version.return_value = False

        result = cfnlint.maintenance.update_resource_spec('us-east-1', 'http://foo.badurl')
        self.assertIsNone(result)
        mock_content.assert_not_called()
        mock_patch_spec.assert_not_called()
        mock_json_dump.assert_not_called()

    @patch('cfnlint.maintenance.multiprocessing.Pool')
    @patch('cfnlint.maintenance.update_resource_spec')
    @patch('cfnlint.maintenance.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_update_resource_specs_python_3(self, mock_update_resource_spec, mock_pool):

        fake_pool = MagicMock()
        mock_pool.return_value.__enter__.return_value = fake_pool

        cfnlint.maintenance.update_resource_specs()

        fake_pool.starmap.assert_called_once()

    @patch('cfnlint.maintenance.multiprocessing.Pool')
    @patch('cfnlint.maintenance.update_resource_spec')
    @patch('cfnlint.maintenance.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_update_resource_specs_python_2(self, mock_update_resource_spec, mock_pool):

        fake_pool = MagicMock()
        mock_pool.return_value.__enter__.return_value = AttributeError('foobar')

        cfnlint.maintenance.update_resource_specs()

        mock_update_resource_spec.assert_called_once_with('us-east-1', 'http://foo.badurl')
