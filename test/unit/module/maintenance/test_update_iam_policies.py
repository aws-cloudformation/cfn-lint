"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
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

        services = [
            {
                "service": "foo",
                "url": "https://servicereference.us-east-1.amazonaws.com/v1/foo/foo.json",
            }
        ]

        cloudformation = {
            "Name": "cloudformation",
            "Actions": [
                {
                    "Name": "CreateStack",
                    "ActionConditionKeys": [
                        "aws:RequestTag/${TagKey}",
                        "aws:TagKeys",
                        "cloudformation:ResourceTypes",
                        "cloudformation:RoleArn",
                        "cloudformation:StackPolicyUrl",
                        "cloudformation:TemplateUrl",
                    ],
                    "Resources": [{"Name": "stack"}],
                }
            ],
            "Resources": [
                {
                    "Name": "stack",
                    "ARNFormats": [
                        "arn:${Partition}:cloudformation:${Region}:${Account}:stack/${StackName}/${Id}"
                    ],
                    "ConditionKeys": ["aws:ResourceTag/${TagKey}"],
                },
                {
                    "Name": "stackset",
                    "ARNFormats": [
                        "arn:${Partition}:cloudformation:${Region}:${Account}:${StackSetName}"
                    ],
                },
            ],
        }

        mock_content.side_effect = [
            json.dumps(services),
            json.dumps(cloudformation),
        ]

        builtin_module_name = "builtins"

        with patch("{}.open".format(builtin_module_name)) as mock_builtin_open:
            cfnlint.maintenance.update_iam_policies()
            mock_json_dump.assert_called_with(
                {
                    "foo": {
                        "Actions": {"createstack": {"Resources": ["stack"]}},
                        "Resources": {
                            "stack": {
                                "ARNFormats": [
                                    "arn:${Partition}:cloudformation:${Region}:${Account}:stack/.*"
                                ],
                                "ConditionKeys": ["aws:ResourceTag/${TagKey}"],
                            },
                            "stackset": {
                                "ARNFormats": [
                                    "arn:${Partition}:cloudformation:${Region}:${Account}:.*"
                                ]
                            },
                        },
                    }
                },
                mock_builtin_open.return_value.__enter__.return_value,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )
