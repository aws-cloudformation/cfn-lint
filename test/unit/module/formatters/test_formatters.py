"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import sys
from pathlib import Path
from test.testlib.testcase import BaseTestCase

import defusedxml.ElementTree as ET

import cfnlint.config
import cfnlint.formatters
import cfnlint.helpers
from cfnlint import ConfigMixIn
from cfnlint.formatters import (
    Formatter,
    JsonFormatter,
    JUnitFormatter,
    ParseableFormatter,
    PrettyFormatter,
    QuietFormatter,
    SARIFFormatter,
)
from cfnlint.jsonschema import StandardValidator
from cfnlint.rules import Match, Rules
from cfnlint.rules.functions.SubUnneeded import SubUnneeded
from cfnlint.rules.resources.properties.Type import Type
from cfnlint.rules.resources.UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes import (
    UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes,
)


class TestFormatters(BaseTestCase):
    """Test Formatters"""

    def setUp(self) -> None:
        super().setUp()
        self.rules = Rules.create_from_directory(cfnlint.config._DEFAULT_RULESDIR)
        self.filename = str(Path("test/fixtures/templates/bad/formatters.yaml"))
        self.sarif_schema = str(Path("test/fixtures/schemas/sarif/schema-2.1.0.json"))
        self.config = ConfigMixIn(
            cli_args=[
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--",
                self.filename,
            ]
        )

        self.results = [
            Match(
                linenumber=6,
                columnnumber=3,
                linenumberend=6,
                columnnumberend=10,
                filename=self.filename,
                rule=UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(),
                message=(
                    "The default action when replacing/removing a resource is to delete"
                    " it. Set explicit values for UpdateReplacePolicy / DeletionPolicy"
                    " on potentially stateful resource: Resources/myTable"
                ),
            ),
            Match(
                linenumber=9,
                columnnumber=7,
                linenumberend=9,
                columnnumberend=16,
                filename=self.filename,
                rule=SubUnneeded(),
                message=(
                    "Fn::Sub isn't needed because there are no variables at"
                    " Resources/myTable/Properties/TableName/Fn::Sub"
                ),
            ),
            Match(
                linenumber=18,
                columnnumber=9,
                linenumberend=18,
                columnnumberend=27,
                filename=self.filename,
                rule=Type(),
                message="'5' is not of type 'integer'",
            ),
        ]

    def test_base_formatter(self):
        """Test base formatter"""
        formatter = Formatter()
        a_results = formatter.print_matches(
            self.results, self.rules, self.config
        ).splitlines()

        # Check the errors
        self.assertEqual(
            a_results[0], f"{self.results[0].rule.id} {self.results[0].message}"
        )
        self.assertEqual(
            a_results[1],
            f"{self.results[0].filename}:{self.results[0].linenumber}:{self.results[0].columnnumber}",
        )
        self.assertEqual(a_results[2], "")
        self.assertEqual(
            a_results[3], f"{self.results[1].rule.id} {self.results[1].message}"
        )
        self.assertEqual(
            a_results[4],
            f"{self.results[1].filename}:{self.results[1].linenumber}:{self.results[1].columnnumber}",
        )
        self.assertEqual(a_results[5], "")
        self.assertEqual(
            a_results[6], f"{self.results[2].rule.id} {self.results[2].message}"
        )
        self.assertEqual(
            a_results[7],
            f"{self.results[2].filename}:{self.results[2].linenumber}:{self.results[2].columnnumber}",
        )

    def test_quiet_formatter(self):
        """Test quiet formatter"""

        formatter = QuietFormatter()
        a_results = formatter.print_matches(
            self.results, self.rules, self.config
        ).splitlines()

        for i in range(3):
            # Check the errors
            # ruff: noqa: E501
            self.assertEqual(
                a_results[i],
                (
                    f"{self.results[i].rule.id}:"
                    f" {self.results[i].rule.shortdesc} {self.results[i].filename}:{self.results[i].linenumber}"
                ),
            )

    def test_parseable_formatter(self):
        """Test Parseable formatter"""
        formatter = ParseableFormatter()
        results = formatter.print_matches(
            self.results, self.rules, self.config
        ).splitlines()

        for i in range(3):
            # Check the errors
            self.assertEqual(
                results[i],
                f"{self.results[i].filename}:{self.results[i].linenumber}:{self.results[i].columnnumber}:{self.results[i].linenumberend}:{self.results[i].columnnumberend}:{self.results[i].rule.id}:{self.results[i].message}",
            )

    def test_pretty_formatter(self):
        """Test pretty formatter"""
        formatter = PrettyFormatter()
        results = formatter.print_matches(
            self.results, rules=self.rules, config=self.config
        ).splitlines()

        if sys.stdout.isatty():
            # Check the errors
            self.assertEqual(results[0], f"\x1b[4m{self.filename}\x1b[0m")
            self.assertEqual(
                results[1],
                (
                    f"\x1b[0m{self.results[2].linenumber}:{self.results[2].columnnumber}:"
                    f"               \x1b[0m\x1b[31m{self.results[2].rule.id}    "
                    f" \x1b[0m{self.results[2].message}"
                ),
            )
            self.assertEqual(
                results[2],
                (
                    f"\x1b[0m{self.results[1].linenumber}:{self.results[1].columnnumber}:"
                    f"                \x1b[0m\x1b[33m{self.results[1].rule.id}    "
                    f" \x1b[0m{self.results[1].message}"
                ),
            )
            self.assertEqual(
                results[3],
                (
                    f"\x1b[0m{self.results[0].linenumber}:{self.results[0].columnnumber}:"
                    f"                \x1b[0m\x1b[34m{self.results[0].rule.id}    "
                    f" \x1b[0m{self.results[0].message}"
                ),
            )
        else:
            # Check the errors
            self.assertEqual(results[0], self.filename)
            self.assertEqual(
                results[1],
                (
                    f"{self.results[2].linenumber}:{self.results[2].columnnumber}:     "
                    f"          {self.results[2].rule.id}     {self.results[2].message}"
                ),
            )
            self.assertEqual(
                results[2],
                (
                    f"{self.results[1].linenumber}:{self.results[1].columnnumber}:     "
                    f"           {self.results[1].rule.id}    "
                    f" {self.results[1].message}"
                ),
            )
            self.assertEqual(
                results[3],
                (
                    f"{self.results[0].linenumber}:{self.results[0].columnnumber}:     "
                    f"           {self.results[0].rule.id}    "
                    f" {self.results[0].message}"
                ),
            )

    def test_pretty_formatter_pipe(self):
        """Test pretty formatter"""
        formatter = PrettyFormatter()
        self.config.cli_args.templates = None
        results = formatter.print_matches(
            self.results, rules=self.rules, config=self.config
        ).splitlines()

        if sys.stdout.isatty():
            self.assertIn("Cfn-lint scanned 1 templates", results[5])
        else:
            # Check the errors
            self.assertIn("Cfn-lint scanned 1 templates", results[5])

    def test_json_formatter(self):
        """Test JSON formatter"""
        formatter = JsonFormatter()

        # Get the JSON output
        json_results = json.loads(
            formatter.print_matches(self.results, self.rules, self.config)
        )

        # Check the 3 errors again
        self.assertEqual(len(json_results), 3)

        # Check the errors level description
        for i in range(3):
            self.assertEqual(json_results[i]["Rule"]["Id"], self.results[i].rule.id)
            self.assertEqual(json_results[i]["Message"], self.results[i].message)

    def test_junit_returns_none(self):
        """Test JUnut Formatter returns None if no rules are passed in"""
        formatter = JUnitFormatter()

        # The actual test
        self.assertIsNone(formatter.print_matches([], [], self.config))

    def test_junit_formatter(self):
        """Test JUnit Formatter"""
        formatter = JUnitFormatter()

        self.rules._used_rules = {
            "I3011": self.rules["I3011"],
            "E3012": self.rules["E3012"],
            "W1020": self.rules["W1020"],
        }
        s = formatter.print_matches(self.results, self.rules, self.config)
        root = ET.fromstring(s)

        self.assertEqual(root.tag, "testsuites")
        self.assertEqual(root[0].tag, "testsuite")

        found_i3011 = False
        found_w1020 = False
        found_e3012 = False
        name_i3011 = "{0} {1}".format(
            self.results[0].rule.id, self.results[0].rule.shortdesc
        )
        name_w1020 = "{0} {1}".format(
            self.results[1].rule.id, self.results[1].rule.shortdesc
        )
        name_e3012 = "{0} {1}".format(
            self.results[2].rule.id, self.results[2].rule.shortdesc
        )
        name_e1029 = "E1029 Sub is required if a variable is used in a string"
        for child in root[0]:
            self.assertEqual(child.tag, "testcase")

            if child.attrib["name"] in [name_i3011, name_w1020, name_e3012]:
                self.assertEqual(child[0].tag, "failure")

                if child.attrib["name"] == name_i3011:
                    found_i3011 = True
                if child.attrib["name"] == name_w1020:
                    found_w1020 = True
                if child.attrib["name"] == name_e3012:
                    found_e3012 = True

            if child.attrib["name"] == name_e1029:
                self.assertEqual(child[0].tag, "skipped")
                self.assertEqual(child[0].attrib["type"], "skipped")

        self.assertTrue(found_i3011)
        self.assertTrue(found_w1020)
        self.assertTrue(found_e3012)

    def test_sarif_formatter(self):
        """Test the SARIF formatter"""
        formatter = SARIFFormatter()

        # Get the SARIF JSON output
        sarif = json.loads(
            formatter.print_matches(self.results, self.rules, self.config)
        )

        with open(self.sarif_schema, encoding="utf-8") as f:
            schema = json.load(f)
        # Fetch the SARIF schema
        # schema = json.loads(cfnlint.helpers.get_url_content(sarif["$schema"], False))
        validator = StandardValidator(schema=schema)
        validator.validate(sarif)

        sarif_results = sarif["runs"][0]["results"]
        # Check the 3 errors again
        self.assertEqual(len(sarif_results), 3)

        # Sanity check the errors
        self.assertEqual(sarif_results[0]["level"], "note")
        self.assertEqual(sarif_results[0]["ruleId"], "I3011")
        # IMPORTANT: 'warning' is the default level in SARIF (when kind is
        # absent) and is stripped by serialization
        self.assertNotIn("level", sarif_results[1].keys())
        self.assertEqual(sarif_results[1]["ruleId"], "W1020")
        self.assertEqual(sarif_results[2]["level"], "error")
        self.assertEqual(sarif_results[2]["ruleId"], "E3012")
