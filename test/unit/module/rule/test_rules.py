"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint import ConfigMixIn, Template
from cfnlint.decode.mark import Mark
from cfnlint.decode.node import dict_node
from cfnlint.exceptions import DuplicateRuleError
from cfnlint.rules import CloudFormationLintRule, Match, RuleMatch, Rules
from cfnlint.rules.errors import RuleError


class Rule(CloudFormationLintRule):
    """Def Rule"""

    id = "EXXXX"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/"
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
    source_url = "https://github.com/aws-cloudformation/cfn-lint/"
    tags = ["resources"]

    def match(self, cfn):
        raise KeyError("Bad template")


class RuleChild(CloudFormationLintRule):
    id = "ECCCC"
    shortdesc = "Child Rule"
    description = "Child Rule"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/"
    tags = ["resources"]

    def validate(self, cfn):
        return [RuleMatch([], "Child Rule", rule=self)]


class RuleParent(CloudFormationLintRule):
    id = "EPPPP"
    shortdesc = "Parent Rule"
    description = "Parent Rule"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__()
        self.child_rules = {
            "ECCCC": RuleChild(),
        }

    def match(self, cfn):
        return [RuleMatch([], "Parent Rule")] + self.child_rules["ECCCC"].validate(cfn)


class TestRules(BaseTestCase):
    """Test CloudFormation Rules"""

    def test_rule_failure(self):
        rules = Rules()
        rules.extend([RuleFail(), RuleError()])

        cfn = Template("-", {}, regions=["us-east-1"])

        matches = list(rules.run("-", cfn, ConfigMixIn([])))
        self.assertListEqual(
            [
                Match(
                    linenumber=1,
                    linenumberend=1,
                    columnnumber=1,
                    columnnumberend=2,
                    filename="-",
                    rule=RuleError(),
                    message=(
                        "Unknown exception while processing rule "
                        "EYYYY: \"'Bad template'\""
                    ),
                )
            ],
            matches,
        )

    def test_parent_child(self):
        rules = Rules()
        rules.extend([RuleParent(), RuleChild()])

        cfn = Template(
            "-", dict_node({}, Mark(0, 0), Mark(0, 0)), regions=["us-east-1"]
        )

        matches = list(rules.run("-", cfn, ConfigMixIn([])))
        self.assertListEqual(
            [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename="-",
                    rule=RuleParent(),
                    message="Parent Rule",
                ),
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename="-",
                    rule=RuleChild(),
                    message="Child Rule",
                ),
            ],
            matches,
            matches,
        )

    def test_parent_child_ignore(self):
        rules = Rules()
        rules.extend([RuleParent(), RuleChild()])

        cfn = Template(
            "-", dict_node({}, Mark(0, 0), Mark(0, 0)), regions=["us-east-1"]
        )

        matches = list(
            rules.run(
                "-", cfn, ConfigMixIn(ignore_checks=["E"], mandatory_checks=["ECCCC"])
            )
        )
        self.assertListEqual(
            [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename="-",
                    rule=RuleChild(),
                    message="Child Rule",
                )
            ],
            matches,
            matches,
        )

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
