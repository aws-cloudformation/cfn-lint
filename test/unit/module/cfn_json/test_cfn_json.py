"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

from six import StringIO

import cfnlint.decode.cfn_json  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.template import Template  # pylint: disable=E0401


class TestCfnJson(BaseTestCase):
    """Test JSON Parsing"""

    def setUp(self):
        """SetUp template object"""
        self.rules = RulesCollection(include_experimental=True)
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            "config_rule": {
                "filename": "test/fixtures/templates/quickstart/config-rules.json",
                "failures": 5,
            },
            "iam": {
                "filename": "test/fixtures/templates/quickstart/iam.json",
                "failures": 5,
            },
            "nat_instance": {
                "filename": "test/fixtures/templates/quickstart/nat-instance.json",
                "failures": 2,
            },
            "vpc_management": {
                "filename": "test/fixtures/templates/quickstart/vpc-management.json",
                "failures": 8,
            },
            "vpc": {
                "filename": "test/fixtures/templates/quickstart/vpc.json",
                "failures": 0,
            },
            "poller": {
                "filename": "test/fixtures/templates/public/lambda-poller.json",
                "failures": 1,
            },
        }

    def test_success_parse(self):
        """Test Successful JSON Parsing"""
        for _, values in self.filenames.items():
            filename = values.get("filename")
            failures = values.get("failures")

            template = cfnlint.decode.cfn_json.load(filename)
            cfn = Template(filename, template, ["us-east-1"])

            matches = []
            matches.extend(self.rules.run(filename, cfn))
            assert (
                len(matches) == failures
            ), "Expected {} failures, got {} on {}".format(
                failures, len(matches), filename
            )

    def test_success_escape_character(self):
        """Test Successful JSON Parsing"""
        failures = 1
        filename = "test/fixtures/templates/good/decode/parsing.json"
        template = cfnlint.decode.cfn_json.load(filename)
        cfn = Template(filename, template, ["us-east-1"])

        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert len(matches) == failures, "Expected {} failures, got {} on {}".format(
            failures, len(matches), filename
        )

    def test_success_parse_stdin(self):
        """Test Successful JSON Parsing through stdin"""
        for _, values in self.filenames.items():
            filename = None
            failures = values.get("failures")
            with open(values.get("filename"), "r") as fp:
                file_content = fp.read()
            with patch("sys.stdin", StringIO(file_content)):
                template = cfnlint.decode.cfn_json.load(filename)
                cfn = Template(filename, template, ["us-east-1"])

                matches = []
                matches.extend(self.rules.run(filename, cfn))
                assert (
                    len(matches) == failures
                ), "Expected {} failures, got {} on {}".format(
                    failures, len(matches), values.get("filename")
                )

    def test_fail_run(self):
        """Test failure run"""

        filename = "test/fixtures/templates/bad/json_parse.json"

        try:
            template = cfnlint.decode.cfn_json.load(filename)
        except cfnlint.decode.cfn_json.JSONDecodeError:
            assert True
            return

        assert False
