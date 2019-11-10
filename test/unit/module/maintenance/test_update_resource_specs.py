"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging
from test.testlib.testcase import BaseTestCase
from mock import patch
import cfnlint.maintenance

LOGGER = logging.getLogger('cfnlint.maintenance')
LOGGER.addHandler(logging.NullHandler())


class TestUpdateResourceSpecs(BaseTestCase):
    """Used for Testing Resource Specs"""
    @patch('cfnlint.maintenance.get_url_content')
    @patch('cfnlint.maintenance.json.dump')
    @patch('cfnlint.maintenance.patch_spec')
    @patch('cfnlint.maintenance.SPEC_REGIONS', {'us-east-1': 'http://foo.badurl'})
    def test_update_resource_specs(self, mock_patch_spec, mock_json_dump, mock_content):
        """Success update resource specs"""

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
            cfnlint.maintenance.update_resource_specs()
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
