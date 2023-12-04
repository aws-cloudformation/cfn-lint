"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint import ConfigMixIn
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules
from cfnlint.runner import TemplateRunner


class TestCustomRuleParsing(BaseTestCase):
    """Test Node Objects"""

    def setUp(self):
        """SetUp template object"""
        self.rules = Rules()
        rulesdirs = [_DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.rules.create_from_directory(rulesdir)

        self.filenames = {
            "generic_good": {"filename": "test/fixtures/templates/good/generic.yaml"}
        }

        self.perfect_rule = "test/fixtures/custom_rules/good/custom_rule_perfect.txt"
        self.valid_boolean = "test/fixtures/custom_rules/good/custom_rule_boolean.txt"
        self.invalid_boolean = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_boolean.txt"
        )
        self.invalid_op = "test/fixtures/custom_rules/bad/custom_rule_invalid_op.txt"
        self.invalid_prop = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_prop.txt"
        )
        self.invalid_propkey = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_propkey.txt"
        )
        self.invalid_rt = "test/fixtures/custom_rules/bad/custom_rule_invalid_rt.txt"
        self.invalid_equal = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_equal.txt"
        )
        self.invalid_not_equal = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_not_equal.txt"
        )
        self.invalid_set = "test/fixtures/custom_rules/bad/custom_rule_invalid_set.txt"
        self.invalid_not_set = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_not_set.txt"
        )
        self.invalid_greater_than = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_greater_than.txt"
        )
        self.invalid_less_than = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_less_than.txt"
        )
        self.invalid_regex = (
            "test/fixtures/custom_rules/bad/custom_rule_invalid_regex.txt"
        )

    def test_perfect_parse(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.perfect_rule) == []

    def test_invalid_op(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.invalid_op)[0].message.find("not in supported") > -1

    def test_invalid_set(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.invalid_set)[0].message.find("In set check") > -1

    def test_invalid_not_set(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.invalid_not_set)[0].message.find("Not in set") > -1

    def test_invalid_equal(self):
        """Test Successful Custom_Rule Parsing"""
        assert (
            self.run_tests(self.invalid_equal)[0].message.find("Must equal check") > -1
        )

    def test_invalid_not_equal(self):
        """Test Successful Custom_Rule Parsing"""
        assert (
            self.run_tests(self.invalid_not_equal)[0].message.find("Must not equal")
            > -1
        )

    def test_invalid_greater_than(self):
        """Test Successful Custom_Rule Parsing"""
        assert (
            self.run_tests(self.invalid_greater_than)[0].message.find(
                "Greater than check"
            )
            > -1
        )

    def test_invalid_less_than(self):
        """Test Successful Custom_Rule Parsing"""
        assert (
            self.run_tests(self.invalid_less_than)[0].message.find("Lesser than check")
            > -1
        )

    def test_invalid_regex(self):
        """Test Successful Custom_Rule Parsing"""
        assert (
            self.run_tests(self.invalid_regex)[0].message.find("Regex does not match")
            > -1
        )

    def test_valid_boolean_value(self):
        """Test Boolean values"""
        assert self.run_tests(self.valid_boolean) == []

    def test_invalid_boolean_value(self):
        """Test Boolean values"""
        assert (
            self.run_tests(self.invalid_boolean)[0].message.find(
                "Must equal check failed"
            )
            > -1
        )

    def test_invalid_prop(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.invalid_prop) == []

    def test_invalid_propKey(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.invalid_propkey) == []

    def test_invalid_resource_type(self):
        """Test Successful Custom_Rule Parsing"""
        assert self.run_tests(self.invalid_rt) == []

    def run_tests(self, rulename):
        for _, values in self.filenames.items():
            filename = values.get("filename")
            template = cfnlint.decode.cfn_yaml.load(filename)
            rules = Rules()
            rules.update(rules.create_from_custom_rules_file(rulename))
            runner = TemplateRunner(filename, template, ConfigMixIn({}), rules)
            return list(runner.run())
