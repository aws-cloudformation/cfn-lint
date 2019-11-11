"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.testlib.testcase import BaseTestCase
from cfnlint.rules import RulesCollection
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
import cfnlint.decode.cfn_json  # pylint: disable=E0401


class TestDuplicate(BaseTestCase):
    """Test Duplicates Parsing """

    def setUp(self):
        """ SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

    def test_success_run(self):
        """Test success run"""

        filename = 'test/fixtures/templates/good/generic.yaml'

        try:
            cfnlint.decode.cfn_yaml.load(filename)
        except cfnlint.decode.cfn_yaml.CfnParseError:
            assert(False)
            return

        assert(True)

    def test_fail_json_run(self):
        """Test failure run"""

    def test_fail_run(self):
        """Test failure run"""

        filename = 'test/fixtures/templates/bad/duplicate.json'

        try:
            with open(filename) as fp:
                json.load(fp, cls=cfnlint.decode.cfn_json.CfnJSONDecoder)
        except cfnlint.decode.cfn_json.JSONDecodeError:
            assert(True)
            return

        assert(False)

    def test_fail_yaml_run(self):
        """Test failure run"""

        filename = 'test/fixtures/templates/bad/duplicate.yaml'

        try:
            cfnlint.decode.cfn_yaml.load(filename)
        except cfnlint.decode.cfn_yaml.CfnParseError:
            assert(True)
            return

        assert(False)
