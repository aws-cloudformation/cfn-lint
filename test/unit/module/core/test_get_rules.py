"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
import cfnlint.core
import cfnlint.helpers  # pylint: disable=E0401


class TestGetRules(BaseTestCase):
    """Test Run Checks """

    def test_invalid_rule(self):
        """test invalid rules"""
        err = None
        try:
            cfnlint.core.get_rules(["invalid"], [], [], [])
        except cfnlint.core.UnexpectedRuleException as e:
            err = e
        assert (type(err) == cfnlint.core.UnexpectedRuleException)
