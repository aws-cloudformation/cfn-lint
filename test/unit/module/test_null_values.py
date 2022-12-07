"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase

import cfnlint.decode.cfn_json  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR
from cfnlint.rules import RulesCollection  # pylint: disable=E0401


class TestNulls(BaseTestCase):
    """Test Null Value Parsing"""

    def setUp(self):
        """SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

    def test_success_run(self):
        """Test success run"""

        filename = "test/fixtures/templates/good/generic.yaml"

        try:
            cfnlint.decode.cfn_yaml.load(filename)
        except cfnlint.decode.cfn_yaml.CfnParseError:
            assert False
            return

        assert True

    def test_fail_json_run(self):
        """Test failure run"""
