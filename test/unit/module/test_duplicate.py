"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

import cfnlint.decode.cfn_json  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules


class TestDuplicate(BaseTestCase):
    """Test Duplicates Parsing"""

    def setUp(self):
        """SetUp template object"""
        self.rules = Rules()
        rulesdirs = [_DEFAULT_RULESDIR]
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

    def test_fail_run(self):
        """Test failure run"""

        filename = "test/fixtures/templates/bad/duplicate.json"

        try:
            cfnlint.decode.cfn_json.load(filename)
        except cfnlint.decode.cfn_json.JSONDecodeError as e:
            self.assertEqual(len(e.matches), 3)
            return

        assert False

    def test_fail_yaml_run(self):
        """Test failure run"""

        filename = "test/fixtures/templates/bad/duplicate.yaml"

        try:
            cfnlint.decode.cfn_yaml.load(filename)
        except cfnlint.decode.cfn_yaml.CfnParseError as e:
            self.assertEqual(len(e.matches), 3)
            return

        assert False
