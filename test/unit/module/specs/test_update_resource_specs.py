"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging

import cfnlint.specs

from test.testlib.testcase import BaseTestCase
from mock import patch, MagicMock
import cfnlint.maintenance

LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())


class TestUpdateResourceSpecs(BaseTestCase):
    """Used for Testing Resource Specs"""
    @patch('cfnlint.specs.url_has_newer_version')
    @patch('cfnlint.specs.get_url_content')
    @patch('cfnlint.maintenance.json.dump')
    @patch('cfnlint.specs.patch_spec')
    @patch('cfnlint.specs.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_update_resource_spec(self, mock_patch_spec, mock_json_dump, mock_content, mock_url_newer_version):
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
                        'm2.medium']
                }
            },
        ]

        if sys.version_info.major == 3:
            builtin_module_name = 'builtins'
        else:
            builtin_module_name = '__builtin__'

        with patch('{}.open'.format(builtin_module_name)) as mock_builtin_open:
            cfnlint.specs.update_resource_spec('us-east-1', 'http://foo.badurl')
            mock_json_dump.assert_called_with(
                {
                    'PropertyTypes': {},
                    'ResourceTypes': {},
                    'ValueTypes': {
                        'AWS::EC2::Instance.Types': [
                            'm2.medium'
                        ]
                    }
                },
                mock_builtin_open.return_value.__enter__.return_value,
                indent=2,
                separators=(',', ': '),
                sort_keys=True
            )

    @patch('cfnlint.specs.url_has_newer_version')
    @patch('cfnlint.specs.get_url_content')
    @patch('cfnlint.maintenance.json.dump')
    @patch('cfnlint.specs.patch_spec')
    @patch('cfnlint.specs.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_do_not_update_resource_spec(self, mock_patch_spec, mock_json_dump, mock_content, mock_url_newer_version):
        """Success update resource spec"""

        mock_url_newer_version.return_value = False

        result = cfnlint.specs.update_resource_spec('us-east-1', 'http://foo.badurl')
        self.assertIsNone(result)
        mock_content.assert_not_called()
        mock_patch_spec.assert_not_called()
        mock_json_dump.assert_not_called()

    @patch('cfnlint.specs.multiprocessing.Pool')
    @patch('cfnlint.specs.update_resource_spec')
    @patch('cfnlint.specs.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_update_resource_specs_python_3(self, mock_update_resource_spec, mock_pool):

        fake_pool = MagicMock()
        mock_pool.return_value.__enter__.return_value = fake_pool

        cfnlint.specs.update_resource_specs()

        fake_pool.starmap.assert_called_once()

    @patch('cfnlint.specs.multiprocessing.Pool')
    @patch('cfnlint.specs.update_resource_spec')
    @patch('cfnlint.specs.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_update_resource_specs_python_2(self, mock_update_resource_spec, mock_pool):

        fake_pool = MagicMock()
        mock_pool.return_value.__enter__.return_value = AttributeError('foobar')

        cfnlint.specs.update_resource_specs()

        mock_update_resource_spec.assert_called_once_with('us-east-1', 'http://foo.badurl')
