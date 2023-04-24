"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import sys
import xml.etree.ElementTree as ET
from test.testlib.testcase import BaseTestCase

import jsonschema

import cfnlint.core
import cfnlint.formatters
import cfnlint.helpers
from cfnlint.rules import Match
from cfnlint.rules.functions.SubUnneeded import SubUnneeded
from cfnlint.rules.resources.properties.ValuePrimitiveType import ValuePrimitiveType
from cfnlint.rules.resources.UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes import (
    UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes,
)


class TestFormatters(BaseTestCase):
    """Test Formatters"""

    def setUp(self) -> None:
        super().setUp()
        cfnlint.core._reset_rule_cache()
        self.filename = "test/fixtures/templates/bad/formatters.yaml"
        self.results = [
            Match(
                6,
                3,
                6,
                10,
                self.filename,
                UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(),
                "The default action when replacing/removing a resource is to delete it. Set explicit values for UpdateReplacePolicy / DeletionPolicy on potentially stateful resource: Resources/myTable",
            ),
            Match(
                9,
                7,
                9,
                16,
                self.filename,
                SubUnneeded(),
                "Fn::Sub isn't needed because there are no variables at Resources/myTable/Properties/TableName/Fn::Sub",
            ),
            Match(
                18,
                9,
                18,
                27,
                self.filename,
                ValuePrimitiveType(),
                "Property Resources/myTable/Properties/ProvisionedThroughput/WriteCapacityUnits should be of type Integer",
            ),
        ]

    def _get_results(self, args, s_formatter):
        # Run a broken template
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(args)

        results = []
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)

            results.extend(
                cfnlint.core.run_checks(filename, template, rules, ["us-east-1"])
            )
        # Validate Formatter class initiated
        self.assertEqual(s_formatter, formatter.__class__.__name__)
        # We need 3 errors (Information, Warning, Error)
        self.assertEqual(len(results), 3)

        return (results, args, filenames, formatter)

    def test_base_formatter(self):
        """Test base formatter"""

        (results, _, _, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--include-checks",
                "I",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "Formatter",
        )
        # Get the base format output
        a_results = formatter.print_matches(results).splitlines()

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

        (results, _, _, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "quiet",
                "--include-checks",
                "I",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "QuietFormatter",
        )
        # Get the base format output
        a_results = formatter.print_matches(results).splitlines()

        for i in range(3):
            # Check the errors
            self.assertEqual(
                a_results[i],
                f"{self.results[i].rule.id}: {self.results[i].rule.shortdesc} {self.results[i].filename}:{self.results[i].linenumber}",
            )

    def test_parseable_formatter(self):
        """Test Parseable formatter"""

        (results, _, _, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "parseable",
                "--include-checks",
                "I",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "ParseableFormatter",
        )
        # Get the base format output
        a_results = formatter.print_matches(results).splitlines()

        for i in range(3):
            # Check the errors
            self.assertEqual(
                a_results[i],
                f"{self.results[i].filename}:{self.results[i].linenumber}:{self.results[i].columnnumber}:{self.results[i].linenumberend}:{self.results[i].columnnumberend}:{self.results[i].rule.id}:{self.results[i].message}",
            )

    def test_pretty_formatter(self):
        """Test pretty formatter"""

        (results, args, filenames, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "pretty",
                "--include-checks",
                "I",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "PrettyFormatter",
        )

        rules = None
        for filename in filenames:
            (_, rules, _) = cfnlint.core.get_template_rules(filename, args)

        # Get the base format output
        a_results = formatter.print_matches(results, rules, filenames).splitlines()

        if sys.stdout.isatty():
            # Check the errors
            self.assertEqual(a_results[0], f"\x1b[4m{self.filename}\x1b[0m")
            self.assertEqual(
                a_results[1],
                f"\x1b[0m{self.results[2].linenumber}:{self.results[2].columnnumber}:               \x1b[0m\x1b[31m{self.results[2].rule.id}     \x1b[0m{self.results[2].message}",
            )
            self.assertEqual(
                a_results[2],
                f"\x1b[0m{self.results[1].linenumber}:{self.results[1].columnnumber}:                \x1b[0m\x1b[33m{self.results[1].rule.id}     \x1b[0m{self.results[1].message}",
            )
            self.assertEqual(
                a_results[3],
                f"\x1b[0m{self.results[0].linenumber}:{self.results[0].columnnumber}:                \x1b[0m\x1b[34m{self.results[0].rule.id}     \x1b[0m{self.results[0].message}",
            )
        else:
            # Check the errors
            self.assertEqual(a_results[0], self.filename)
            self.assertEqual(
                a_results[1],
                f"{self.results[2].linenumber}:{self.results[2].columnnumber}:               {self.results[2].rule.id}     {self.results[2].message}",
            )
            self.assertEqual(
                a_results[2],
                f"{self.results[1].linenumber}:{self.results[1].columnnumber}:                {self.results[1].rule.id}     {self.results[1].message}",
            )
            self.assertEqual(
                a_results[3],
                f"{self.results[0].linenumber}:{self.results[0].columnnumber}:                {self.results[0].rule.id}     {self.results[0].message}",
            )

    def test_json_formatter(self):
        """Test JSON formatter"""
        (results, _, _, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "json",
                "--include-checks",
                "I",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "JsonFormatter",
        )

        # Check the errors
        self.assertEqual(results[0].rule.id, "I3011")
        self.assertEqual(results[1].rule.id, "W1020")
        self.assertEqual(results[2].rule.id, "E3012")

        # Get the JSON output
        json_results = json.loads(formatter.print_matches(results))

        # Check the 3 errors again
        self.assertEqual(len(json_results), 3)

        # Check the errors level description
        for i in range(3):
            self.assertEqual(json_results[i]["Rule"]["Id"], self.results[i].rule.id)
            self.assertEqual(json_results[i]["Message"], self.results[i].message)

    def test_junit_returns_none(self):
        """Test JUnut Formatter returns None if no rules are passed in"""

        (results, _, _, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "junit",
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "JUnitFormatter",
        )

        # The actual test
        self.assertIsNone(formatter.print_matches([], []))

    def test_junit_formatter(self):
        """Test JUnit Formatter"""
        (results, _, _, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "junit",
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "JUnitFormatter",
        )

        # Check the errors
        self.assertEqual(results[0].rule.id, "I3011")
        self.assertEqual(results[1].rule.id, "W1020")
        self.assertEqual(results[2].rule.id, "E3012")

        root = ET.fromstring(
            formatter.print_matches(results, cfnlint.core.get_used_rules())
        )

        self.assertEqual(root.tag, "testsuites")
        self.assertEqual(root[0].tag, "testsuite")

        found_i3011 = False
        found_w1020 = False
        found_e3012 = False
        name_i3011 = "{0} {1}".format(results[0].rule.id, results[0].rule.shortdesc)
        name_w1020 = "{0} {1}".format(results[1].rule.id, results[1].rule.shortdesc)
        name_e3012 = "{0} {1}".format(results[2].rule.id, results[2].rule.shortdesc)
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

        (results, args, filenames, formatter) = self._get_results(
            [
                "--template",
                self.filename,
                "--format",
                "sarif",
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--configure-rule",
                "E3012:strict=true",
            ],
            "SARIFFormatter",
        )

        rules = None
        for filename in filenames:
            (_, rules, _) = cfnlint.core.get_template_rules(filename, args)

        # Check the errors
        self.assertEqual(results[0].rule.id, "I3011")
        self.assertEqual(results[1].rule.id, "W1020")
        self.assertEqual(results[2].rule.id, "E3012")

        # Get the SARIF JSON output
        sarif = json.loads(formatter.print_matches(results, rules))

        # Fetch the SARIF schema
        schema = json.loads(cfnlint.helpers.get_url_content(sarif["$schema"], False))
        jsonschema.validate(sarif, schema)

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
