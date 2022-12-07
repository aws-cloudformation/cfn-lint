"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import xml.etree.ElementTree as ET
from test.testlib.testcase import BaseTestCase

import jsonschema

import cfnlint.core
import cfnlint.formatters
import cfnlint.helpers


class TestFormatters(BaseTestCase):
    """Test Formatters"""

    def setUp(self) -> None:
        super().setUp()
        cfnlint.core._reset_rule_cache()

    def test_json_formatter(self):
        """Test JSON formatter"""

        # Run a broken template
        filename = "test/fixtures/templates/bad/formatters.yaml"
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
                "--format",
                "json",
                "--include-checks",
                "I",
                "--configure-rule",
                "E3012:strict=true",
            ]
        )

        results = []
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)

            results.extend(
                cfnlint.core.run_checks(filename, template, rules, ["us-east-1"])
            )

        # Validate Formatter class initiated
        self.assertEqual("JsonFormatter", formatter.__class__.__name__)
        # We need 3 errors (Information, Warning, Error)
        self.assertEqual(len(results), 3)
        # Check the errors
        self.assertEqual(results[0].rule.id, "I3011")
        self.assertEqual(results[1].rule.id, "W1020")
        self.assertEqual(results[2].rule.id, "E3012")

        # Get the JSON output
        json_results = json.loads(formatter.print_matches(results))

        # Check the 3 errors again
        self.assertEqual(len(json_results), 3)

        # Check the errors level description
        self.assertEqual(json_results[0]["Level"], "Informational")
        self.assertEqual(json_results[1]["Level"], "Warning")
        self.assertEqual(json_results[2]["Level"], "Error")

    def test_junit_returns_none(self):
        """Test JUnut Formatter returns None if no rules are passed in"""

        # Test setup
        filename = "test/fixtures/templates/bad/formatters.yaml"
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
                "--format",
                "junit",
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--configure-rule",
                "E3012:strict=true",
            ]
        )

        results = []
        rules = None
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
            results.extend(
                cfnlint.core.run_checks(filename, template, rules, ["us-east-1"])
            )

        # Validate Formatter class initiated
        self.assertEqual("JUnitFormatter", formatter.__class__.__name__)

        # The actual test
        self.assertIsNone(formatter.print_matches([], []))

    def test_junit_formatter(self):
        """Test JUnit Formatter"""

        # Run a broken template
        filename = "test/fixtures/templates/bad/formatters.yaml"
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
                "--format",
                "junit",
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--configure-rule",
                "E3012:strict=true",
            ]
        )

        results = []
        rules = None
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
            results.extend(
                cfnlint.core.run_checks(filename, template, rules, ["us-east-1"])
            )

        # Validate Formatter class initiated
        self.assertEqual("JUnitFormatter", formatter.__class__.__name__)

        # We need 3 errors (Information, Warning, Error)
        self.assertEqual(len(results), 3)
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

        # Run a broken template
        filename = "test/fixtures/templates/bad/formatters.yaml"
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
                "--format",
                "sarif",
                "--include-checks",
                "I",
                "--ignore-checks",
                "E1029",
                "--configure-rule",
                "E3012:strict=true",
            ]
        )

        results = []
        rules = None
        for filename in filenames:
            (template, rules, _) = cfnlint.core.get_template_rules(filename, args)
            results.extend(
                cfnlint.core.run_checks(filename, template, rules, ["us-east-1"])
            )

        # Validate Formatter class initiated
        self.assertEqual("SARIFFormatter", formatter.__class__.__name__)

        # We need 3 errors (Information, Warning, Error)
        self.assertEqual(len(results), 3)
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
