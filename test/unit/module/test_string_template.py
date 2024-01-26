"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

import cfnlint.decode.cfn_json  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401


class TestNonObjectTemplate(BaseTestCase):
    """Test Duplicates Parsing"""

    def setUp(self):
        """SetUp template object"""

    def test_fail_yaml_run(self):
        """Test failure run"""

        filename = "test/fixtures/templates/bad/string.yaml"

        _, matches = cfnlint.decode.decode(filename)
        assert len(matches) == 1
