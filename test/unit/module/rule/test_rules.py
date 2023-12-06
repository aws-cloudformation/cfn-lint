"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

from cfnlint import ConfigMixIn, Template
from cfnlint.rules import CloudFormationLintRule, DuplicateRuleError, RuleError, Rules


class Rule(CloudFormationLintRule):
    """Def Rule"""

    id = "EXXXX"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
    tags = ["resources"]

    def __init__(self):
        """Init"""
        super(Rule, self).__init__()
        self.config_definition = {
            "testBoolean": {"default": True, "type": "boolean"},
            "testString": {"default": "default", "type": "string"},
            "testInteger": {"default": 1, "type": "integer"},
        }
        self.configure()

    def get_config(self):
        """Get the Config"""
        return self.config


class RuleFail(CloudFormationLintRule):
    """Def Rule"""

    id = "EYYYY"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/"
    tags = ["resources"]

    def match(self, cfn):
        raise KeyError("Bad template")


class TestRules(BaseTestCase):
    """Test CloudFormation Rules"""

    def test_rule_failure(self):
        rules = Rules()
        rules.extend([RuleFail(), RuleError()])

        cfn = Template("-", {}, regions=["us-east-1"])

        matches = list(rules.run("-", cfn, ConfigMixIn([])))
        self.assertListEqual([], matches)

    def test_rule_deletion(self):
        rules = Rules()
        rules.extend([Rule()])

        with self.assertRaises(RuntimeError):
            del rules["EXXXX"]

    def test_failure_on_duplicate_rule(self):
        rules = Rules()

        with self.assertRaises(DuplicateRuleError):
            rules.extend([Rule(), Rule()])

    def test_custom_rules(self):
        rules = Rules.create_from_custom_rules_file(
            "test/fixtures/custom_rules/good/custom_rule_perfect.txt"
        )

        self.assertEqual(len(rules), 15)
