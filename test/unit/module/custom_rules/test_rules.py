"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
import cfnlint.customRules.Rule


class TestCustomRules(BaseTestCase):
    """Test Rule Objects """

    def test_invalid_rule(self):
        """Test success run"""

        rule = cfnlint.customRules.Rule.make_rule('ABCD')

        assert (rule.valid is False)

    def test_valid_rule(self):
        """Test success run"""

        rule = cfnlint.customRules.Rule.make_rule('AWS::IAM::Role AssumeRolePolicyDocument.Version EQUALS 2020')

        assert (rule.valid is True)
