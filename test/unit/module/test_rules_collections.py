"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

import regex as re

import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
from cfnlint.exceptions import DuplicateRuleError
from cfnlint.rules import CloudFormationLintRule, RulesCollection
from cfnlint.template import Template


class TestRulesCollection(BaseTestCase):
    """Test Template RulesCollection in cfnlint"""

    def setUp(self):
        """SetUp template object"""
        self.rules = RulesCollection()
        self.rules.include_rules = ["I", "W", "E"]
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

    def test_rule_ids_unique(self):
        """Test Rule IDs are Unique"""
        existing_rules = []
        for rule in self.rules:
            self.assertFalse(rule.id in existing_rules)
            existing_rules.append(rule.id)

    def test_rule_ids_are_formatted_correctly(self):
        """Test Rule IDs are property formmated"""
        for rule in self.rules:
            self.assertIn(rule.id[0], ["W", "I", "E"])
            self.assertEqual(len(rule.id), 5)
            self.assertTrue(isinstance(int(rule.id[1:]), int))

    def test_success_run(self):
        """Test Run Logic"""
        filename = "test/fixtures/templates/good/generic.yaml"
        template = cfnlint.decode.cfn_yaml.load(filename)
        cfn = Template(filename, template, ["us-east-1"])

        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert matches == []

    def test_fail_run(self):
        """Test failure run"""
        filename = "test/fixtures/templates/bad/generic.yaml"
        template = cfnlint.decode.cfn_yaml.load(filename)
        cfn = Template(filename, template, ["us-east-1"])
        expected_err_count = 33
        matches = []
        matches.extend(self.rules.run(filename, cfn))
        assert (
            len(matches) == expected_err_count
        ), "Expected {} failures, got {}".format(expected_err_count, len(matches))

    def test_fail_sub_properties_run(self):
        """Test failure run"""
        filename = "test/fixtures/templates/bad/resources/properties/onlyone.yaml"
        template = cfnlint.decode.cfn_yaml.load(filename)
        cfn = Template(filename, template, ["us-east-1"])

        matches = []
        matches.extend(self.rules.run(filename, cfn))
        self.assertEqual(
            6, len(matches), "Expected {} failures, got {}".format(6, len(matches))
        )

    def test_success_filtering_of_rules_default(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""

            id = "W0000"

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""

            id = "I0000"

        rules_to_add = [rule_e0000(), rule_w0000(), rule_i0000()]
        rules = RulesCollection(ignore_rules=None, include_rules=None)
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 2)
        for rule in rules:
            self.assertIn(rule.id, ["W0000", "E0000"])

    def test_success_filtering_of_rules_include_info(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""

            id = "W0000"

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""

            id = "I0000"

        rules_to_add = [rule_e0000(), rule_w0000(), rule_i0000()]
        rules = RulesCollection(ignore_rules=None, include_rules=["I"])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 3)
        for rule in rules:
            self.assertIn(rule.id, ["I0000", "W0000", "E0000"])

    def test_success_filtering_of_rules_exclude(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""

            id = "W0000"

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""

            id = "I0000"

        rules_to_add = [rule_e0000(), rule_w0000(), rule_i0000()]
        rules = RulesCollection(ignore_rules=["E"])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 1)
        for rule in rules:
            self.assertIn(rule.id, ["W0000"])

    def test_success_filtering_of_rules_exclude_long(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_e0010(CloudFormationLintRule):
            """Error Rule"""

            id = "E0010"

        class rule_e0002(CloudFormationLintRule):
            """Error Rule"""

            id = "E0002"

        rules_to_add = [rule_e0000(), rule_e0010(), rule_e0002()]
        rules = RulesCollection(ignore_rules=["E000"])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 1)
        for rule in rules:
            self.assertIn(rule.id, ["E0010"])

    def test_success_filtering_of_rules_exclude_longer(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_e0010(CloudFormationLintRule):
            """Error Rule"""

            id = "E0010"

        class rule_e0002(CloudFormationLintRule):
            """Error Rule"""

            id = "E0002"

        rules_to_add = [rule_e0000(), rule_e0010(), rule_e0002()]
        rules = RulesCollection(ignore_rules=["E0002"])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 2)
        for rule in rules:
            self.assertIn(rule.id, ["E0000", "E0010"])

    def test_success_filtering_of_rules_exclude_mandatory(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""

            id = "W0000"

        class rule_i0000(CloudFormationLintRule):
            """Info Rule"""

            id = "I0000"

        rules_to_add = [rule_e0000(), rule_w0000(), rule_i0000()]
        rules = RulesCollection(ignore_rules=["E"], mandatory_rules=["E"])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 2)
        for rule in rules:
            self.assertIn(rule.id, ["E0000", "W0000"])

    def test_success_filtering_of_rules_exclude_mandatory_long(self):
        """Test extend function"""

        class rule_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule_e0010(CloudFormationLintRule):
            """Error Rule"""

            id = "E0010"

        class rule_e0002(CloudFormationLintRule):
            """Error Rule"""

            id = "E0002"

        class rule_w0000(CloudFormationLintRule):
            """Warning Rule"""

            id = "W0000"

        rules_to_add = [rule_e0000(), rule_e0010(), rule_e0002(), rule_w0000()]
        rules = RulesCollection(ignore_rules=["E"], mandatory_rules=["E000"])
        rules.extend(rules_to_add)
        self.assertEqual(len(rules), 3)
        for rule in rules:
            self.assertIn(rule.id, ["E0000", "E0002", "W0000"])

    def test_duplicate_rules(self):
        """Test extend function"""

        class rule0_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        class rule1_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"

        rules_to_add = [rule0_e0000(), rule1_e0000()]
        rules = RulesCollection()
        self.assertRaises(DuplicateRuleError, rules.extend, rules_to_add)

    def test_repr(self):
        class rule0_e0000(CloudFormationLintRule):
            """Error Rule"""

            id = "E0000"
            shortdesc = "Rule A"
            description = "First rule"

        class rule1_e0001(CloudFormationLintRule):
            """Error Rule"""

            id = "E0001"
            shortdesc = "Rule B"
            description = "Second rule"

        rules = RulesCollection()
        rules.extend([rule0_e0000(), rule1_e0001()])

        retval = repr(rules)
        pattern = r"\AE0000: Rule A\nFirst rule\nE0001: Rule B\nSecond rule\Z"
        match = re.match(pattern, retval)
        assert match, f"{retval} does not match {pattern}"


class TestCreateFromModule(BaseTestCase):
    """Test loading a rules collection from a module"""

    def test_create_from_module(self):
        """Load rules from a module"""
        rules = RulesCollection()
        rules.create_from_module("cfnlint.rules.templates.Base")
        self.assertIn("E1001", (r.id for r in rules))
