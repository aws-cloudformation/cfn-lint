"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import cfnlint.maintenance

LOGGER = logging.getLogger("cfnlint.maintenance")
LOGGER.addHandler(logging.NullHandler())


class TestUpdateIamPolicies(BaseTestCase):
    """Used for Testing Rules"""

    @patch("cfnlint.maintenance.get_url_content")
    @patch("cfnlint.maintenance.json.dump")
    def test_update_iam_policies(self, mock_json_dump, mock_content):
        """Success update iam policies"""

        mock_content.return_value = (
            'app.PolicyEditorConfig={"serviceMap":{"Manage Amazon API'
            ' Gateway":{"Actions":[]},"Amazon Kinesis Video Streams":{"Actions":[]}}}'
        )

        builtin_module_name = "builtins"

        with patch("{}.open".format(builtin_module_name)) as mock_builtin_open:
            cfnlint.maintenance.update_iam_policies()
            mock_json_dump.assert_called_with(
                {
                    "serviceMap": {
                        "Manage Amazon API Gateway": {"Actions": ["HEAD", "OPTIONS"]},
                        "Amazon Kinesis Video Streams": {
                            "Actions": ["StartStreamEncryption"]
                        },
                    }
                },
                mock_builtin_open.return_value.__enter__.return_value,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )
