"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

from six import StringIO

import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.template import Template  # pylint: disable=E0401


class TestYamlParse(BaseTestCase):
    """Test YAML Parsing"""

    def setUp(self):
        """SetUp template object"""
        self.rules = RulesCollection()
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            "config_rule": {
                "filename": "test/fixtures/templates/public/lambda-poller.yaml",
                "failures": 1,
            },
            "generic_bad": {
                "filename": "test/fixtures/templates/bad/generic.yaml",
                "failures": 30,
            },
        }

    def test_success_parse(self):
        """Test Successful YAML Parsing"""
        for _, values in self.filenames.items():
            filename = values.get("filename")
            failures = values.get("failures")
            template = cfnlint.decode.cfn_yaml.load(filename)
            cfn = Template(filename, template, ["us-east-1"])

            matches = []
            matches.extend(self.rules.run(filename, cfn))
            assert (
                len(matches) == failures
            ), "Expected {} failures, got {} on {}".format(
                failures, len(matches), filename
            )

    def test_success_parse_stdin(self):
        """Test Successful YAML Parsing through stdin"""
        for _, values in self.filenames.items():
            filename = None
            failures = values.get("failures")
            with open(values.get("filename"), "r") as fp:
                file_content = fp.read()

            with patch("sys.stdin", StringIO(file_content)):
                template = cfnlint.decode.cfn_yaml.load(filename)
                cfn = Template(filename, template, ["us-east-1"])

                matches = []
                matches.extend(self.rules.run(filename, cfn))
                assert (
                    len(matches) == failures
                ), "Expected {} failures, got {} on {}".format(
                    failures, len(matches), values.get("filename")
                )

    def test_map_failure(self):
        """Test a failure is passed on unhashable map"""
        filename = "test/fixtures/templates/bad/core/parse_invalid_map.yaml"

        self.assertRaises(
            cfnlint.decode.cfn_yaml.CfnParseError,
            cfnlint.decode.cfn_yaml.load,
            filename,
        )
