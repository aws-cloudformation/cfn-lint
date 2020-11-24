"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import RegexDict
from test.testlib.testcase import BaseTestCase

class TestRegexDict(BaseTestCase):
    """Test Regex Dict """

    def test_success_run(self):
        """Test success run"""

        obj = RegexDict()
        obj['^Value$'] = True

        with self.assertRaises(KeyError):
            obj['NotExist']
