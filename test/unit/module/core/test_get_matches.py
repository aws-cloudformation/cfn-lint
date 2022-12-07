"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
from test.testlib.testcase import BaseTestCase

import cfnlint.core
import cfnlint.helpers  # pylint: disable=E0401


class TestGetMatches(BaseTestCase):
    """Test Get Matches"""

    def test_multiple_templates(self):
        """test multiple templates"""

        filenames = [
            "test/fixtures/templates/bad/noecho.yaml",
            "test/fixtures/templates/bad/issues.yaml",
        ]

        (args, filenames, _) = cfnlint.core.get_args_filenames(filenames)
        matches = cfnlint.core.get_matches(filenames, args)
        self.assertEqual(
            ["E1012", "W4002", "W4002"], [match.rule.id for match in matches]
        )
