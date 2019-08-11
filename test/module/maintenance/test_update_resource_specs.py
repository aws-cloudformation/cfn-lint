"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import sys
import logging
from mock import patch
import cfnlint.maintenance
from testlib.testcase import BaseTestCase

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
